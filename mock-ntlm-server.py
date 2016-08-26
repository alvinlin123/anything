#! /usr/bin/python

#This mock server will challenge the client with NTLM auth and only authorize the 
#client if the user name and domain name sent by the client equals to the predefined
#value. This mock was tailor made to a piece of code I was trying to test.

#reference http://davenport.sourceforge.net/ntlm.html#ntlmHttpAuthentication

import sys
import BaseHTTPServer
import base64

goodUser = "ntlmuser"
goodDomain = "ntlmdomain"

def bytesToInt(bytes):
    result = 0
    shift = 0

    #fields in ntlm messages  are in little edian (higher byte is less significant)...
    for b in bytes:
        result += b << shift
        shift += 8
    return result

def getNtlmMsgType(encoded):
    decoded = bytearray(base64.b64decode(encoded))
    print "type is " + str(decoded[8])
    return decoded[8];

#input is type 3 ntlm message in base64 encoded format
def getNtlmDomainName(encoded): 
    decoded = bytearray(base64.b64decode(encoded))
    offset = bytesToInt(decoded[28+4 : 28+8])
    print "domain data offset is " + str(offset)
    length = bytesToInt(decoded[28 : 28 +2])
    print "domain data length is " + str(length)
    domainData = decoded[offset : offset + length]
    
    givenDomainName = ""
    for i in domainData:
        if i > 0:
            givenDomainName += chr(i)

    givenDomainName = givenDomainName.lower()
    print "given domain name is " + givenDomainName
    return givenDomainName

#input is type 3 ntlm message in base64 encoded format
def getNtlmUserName(encoded):
    decoded = bytearray(base64.b64decode(encoded))
    offset = bytesToInt(decoded[(36+4):(36+8)])
    print "user name data offset is " + str(offset)
    length = bytesToInt(decoded[36:(36+2)])
    print "user name data length is " + str(length)
    nameData =  decoded[offset : offset+length]
    givenUserName = ""
    
    #nameData contains double byte char in little edian.. since we only use ASCII
    #we need to filter out the zero-bytes
    for i in nameData:
        if i > 0:
            givenUserName += chr(i)

    print "given user name is " + givenUserName
    return givenUserName

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        print self.command, self.path
        proxyAuthHeader = self.headers.get("Proxy-Authorization")
        if (proxyAuthHeader):
            print "proxy auth header is " + proxyAuthHeader
            encodedAuthData = proxyAuthHeader[len("NTLM "):]
            msgType = getNtlmMsgType(encodedAuthData)
            if (msgType == 1): 
                self.send_response(407)
                self.send_header("Content-Length", "0")
                #The value of the proxy-authenticate is just copy and pasted from some website.
                self.send_header("Proxy-Authenticate", "NTLM TlRMTVNTUAACAAAADAAMADAAAAABAoEAASNFZ4mrze8AAAAAAAAAAGIAYgA8AAAARABPAE0AQQBJAE4AAgAMAEQATwBNAEEASQBOAAEADABTAEUAUgBWAEUAUgAEABQAZABvAG0AYQBpAG4ALgBjAG8AbQADACIAcwBlAHIAdgBlAHIALgBkAG8AbQBhAGkAbgAuAGMAbwBtAAAAAAA=")
                self.end_headers()
            elif (msgType == 3):
                givenUserName = getNtlmUserName(encodedAuthData)
                givenDomainName = getNtlmDomainName(encodedAuthData)
                responseCode = 401
                if givenUserName == goodUser and givenDomainName == goodDomain:
                    responseCode = 200
                self.send_response(responseCode);
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                self.send_response(400, "Unknown NTLM message type")
                self.send_header("Content-Length", "0")
                self.end_headers()
        else:
            self.send_response(407)
            self.send_header("Content-Length", "0")
            self.send_header("Proxy-Authenticate", "NTLM")
            self.end_headers()
        return

ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.1"

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
    server_address = ('127.0.0.1', port)

    MyHandler.protocol_version = Protocol
    httpd = ServerClass(server_address, MyHandler)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
