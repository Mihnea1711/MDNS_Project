import struct

FORMAT = "utf-8"


# # # # # # # # # # # # # # # # # # # # # # # # HEADER # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def format_MDNS_Header(qr, qd_count, an_count):
    # id
    transaction_id = 0  # id pe 16 bits (should be 0 on transmission)

    # flags
    qr_bit = qr
    aa_bit = qr
    flags = f'{qr_bit}0000{aa_bit}0000000000'
    flags = int(flags, 2)

    # info
    qd_count = qd_count
    an_count = an_count
    ns_count = 0        # not necessary
    ar_count = 0        # not necessary

    return struct.pack("!HHHHHH", transaction_id,
                       flags, qd_count, an_count, ns_count, ar_count)


def unpackHeader(message):
    header = struct.unpack_from("!HHHHHH", message, 0)

    flags = header[1]
    qd_count = header[2]
    an_count = header[3]

    return flags, qd_count, an_count


# # # # # # # # # # # # # # # # # # # # # # QUESTION SECTION # # # # # # # # # # # # # # # # # # # # # # # # # #

# in program folosim 2 tipuri de request-uri
# ptr si srv
# in cazul amandurora, formatul este la fel
# se schimba doar modul cum parsam request-ul

# helper to create the names and hostnames list => format: (len label) (len label) (...) 0
def createLabels(name):
    list = []
    for label in name.split("."):
        list.append(len(label))
        list.append(label.encode(FORMAT))
    list.append(0)

    return list


# helper to create the format for the method above ^
def createQNameFormat(name):
    labels = name.split(".")
    qname_format = ''
    for i in range(0, len(labels)):
        qname_format += f'B{len(labels[i])}s'
    qname_format += 'B'  # add short int = 0 la final ca terminator

    return qname_format


def formatQuestionSection(qname, qtype):
    # qname va fi de forma

    # PTR:
    #     _services._dns-sd._udp.local          <= pt lookup for empty string, asta vom trimite ca si query!
    #       sau
    #     _scanner._udp.local                   <= pt lookup for serv

    # SRV:
    #     scanner1._scanner._udp.local          <= pt selectare instanta

    # # # # # # # # # QNAME FORMATTING

    qname_len = len(qname)
    labels = createLabels(qname)
    format = createQNameFormat(qname)
    qname = struct.pack(format, *labels)            # create format and request name

    # # # # # # # # # QTYPE FORMATTING

    if qtype.lower() == 'ptr':
        qtype = 12                  # decimal number for PTR
    elif qtype.lower() == 'srv':
        qtype = 33                  # decimal number for SRV

    # # # # # # # # # QCLASS FORMATTING

    qu_bit = b'0'                           # mereu QM msg (always multicasting it)
    qclass = qu_bit + b'000000000000001'
    qclass = int(qclass, 2)                 # mereu class IN (internet)

    # # # # # # # # # # # # # # # # # # # #

    # + 2 pentru ca
    # scadem nr de puncte dintre ele dar adunam nr de labels (mereu dif va fi +1)
    # + un terminator la final (0)
    return struct.pack(f'!{qname_len + 2}sHH', qname, qtype, qclass)


# create the actual request
def createRequest(query, qr_bit, qtype):
    # pack the header and the question together
    header = format_MDNS_Header(qr_bit, 1, 0)
    question = formatQuestionSection(query, qtype)

    return header + question


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# helper to unpack the name/hostname/..
def unpackName(message, offset):
    labels = []
    flag = True
    while flag:
        label_length = struct.unpack_from("!B", message, offset)[0]
        offset += 1
        label = struct.unpack_from(f"!{label_length}sB", message, offset)
        offset += label_length
        labels.append(label[0].decode(FORMAT))
        if label[1] == 0:
            flag = False
    offset += 1  # name end (1 byte of 0)

    return ".".join(labels), offset


# helper to unpack the query inside a request (return only the actual data and the type: srv/ptr)
def unpackQuery(request):
    offset = 12             # start unpacking after the header

    query, offset = unpackName(request, offset)
    qtype = struct.unpack_from("!H", request, offset)[0]
    # could unpack the other data, but there is no need (can use it for additional checks)

    return query, qtype


# parse the actual request
def parseRequest(request):
    flags, qd_count, an_count = unpackHeader(request)
    query, qtype = unpackQuery(request)

    return flags, qd_count, an_count, query, qtype


# # # # # # # # # # # # # # # # # # # # # # # # # # # RESPONSE SECTION # # # # # # # # # # # # # # # # # # # # # #

# folosim acelasi header, dar qr_bit va fi 1 de data asta

# avem 4 tipuri de raspunsuri
# srv / ptr / a / txt

# ########################################### Simple Response #######################################################

# type A
def formatTypeA(name, ip, ttl):
    # name: label_len, label, [.., .., ..,] (0 sau compr pointer)
    # type A: (1)
    # class in
    # ttl ...
    # data length: 4
    # address: ...
    # name_compression_pointer = int("1100000000000000", 2)  # wut is this (don't need it)

    # hostname va avea forma scanner1.local
    hostname, domain_name = name.split(".")
    rname_components = createLabels(name)

    # type A => 1
    rtype = 1

    # everytime we get type A response, we flush the record from the cache
    cache_flush_bit = 1
    rclass = int(f"{cache_flush_bit}000000000000001", 2)

    # format the ip ( data part )
    ip_parts = list(map(lambda part: int(part), ip.split(".")))
    data_length = len(ip_parts)

    return struct.pack(f"!B{len(hostname)}sB{len(domain_name)}sBHHIHBBBB", *rname_components, rtype, rclass, ttl,
                       data_length, *ip_parts)


# create the actual type A response
def createResponse_TypeA(hostname, ip, ttl):
    # pack the header and the A response
    header = format_MDNS_Header(1, 0, 1)
    answer = formatTypeA(hostname, ip, ttl)

    return header + answer


# type PTR
def formatTypePTR(name, service, ttl):
    # name: label_len, label, [.., .., ..,] (0 sau compr pointer)
    # type PTR: (12)
    # class in cache flush 0
    # ttl ...
    # data length: 4
    # 'domain name': instance + proto + domain

    # name va fi de forma: hostname._protocol.local     # pot fi mai multe protocoale, noi folosim doar udp
    # aici hostname si instance cam difera, dar le-am folosit ca fiind acelasi lucru din simplitate
    hostname, protocol, domain_name = name.split(".")
    rname_components = createLabels(name)

    # type PTR => 12
    rtype = 12

    # don't need to flush anything from cache
    cache_flush_bit = 0
    rclass = int(f"{cache_flush_bit}000000000000001", 2)

    # + 1 => 0 at the end
    # data => scanner1._scanner._udp.local
    data_length = (len(hostname) + 1) + (len(service) + 1) + (len(protocol) + 1) + (len(domain_name) + 1) + 1
    data = f"{hostname}.{service}.{protocol}.{domain_name}"
    data_components = createLabels(data)

    return \
        struct.pack(
            f"!B{len(hostname)}sB{len(protocol)}sB{len(domain_name)}sBHHIHB{len(hostname)}sB{len(service)}sB{len(protocol)}sB{len(domain_name)}sB",
            *rname_components, rtype, rclass, ttl, data_length, *data_components)


# create the actual PTR response
def createResponse_TypePTR(hostname, service, ttl):
    # pack the header and the PTR response
    header = format_MDNS_Header(1, 0, 1)
    answer = formatTypePTR(hostname, service, ttl)

    return header + answer


# unpack any of typeA or typePTR
# unpacking is similar, the only thing that is different is the content of the data field
def unpackSimpleResponse(response):
    offset = 12
    rname, offset = unpackName(response, offset)

    rtype = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    rclass = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    ttl = struct.unpack_from("!I", response, offset)[0]
    offset += 4

    data_length = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    data = ''
    if rtype == 12:
        # type ptr
        data, _ = unpackName(response, offset)
    elif rtype == 1:
        # type A
        data = []
        while data_length:
            ip_part = struct.unpack_from("!B", response, offset)[0]
            data.append(str(ip_part))
            offset += 1
            data_length -= 1
        data = ".".join(data)

    return rname, rtype, rclass, ttl, data


# parse simple response (type A or type PTR)
def parseSimpleResponse(response):
    flags, qd_count, an_count = unpackHeader(response)
    if an_count == 1:
        rname, rtype, rclass, ttl, data = unpackSimpleResponse(response)
        return rname, rtype, rclass, ttl, data
    else:
        pass


# ########################################### Complex Response #######################################################

# type SRV
def formatTypeSRV(name, target, port, ttl):
    # service + protocol + domain:
    # type SRV => 33
    # rclass => cache_flush + 0x0001 (IN)
    # ttl ..
    # data length
    # priority 0
    # weight 0
    # port ? (current port ig)
    # target: hostname

    # name va fi de forma: _scanner._udp.local
    service, protocol, domain_name = name.split(".")
    rservice_components = createLabels(name)

    # SRV => 33
    rtype = 33

    # always flush the cache when this gets received
    cache_flush_bit = 1
    rclass = int(f"{cache_flush_bit}000000000000001", 2)

    # data length = 2bytes for priority + 2bytes for weight + 2bytes for port + target_length + 1 (0 at the end)
    # target will look like this: hostname.local
    hostname, _ = target.split(".")
    data_length = 2 + 2 + 2 + (len(target) + 1)

    # these are not used
    priority = 0
    weight = 0
    # port = current port
    rtarget_components = createLabels(target)

    return struct.pack(
        f"!B{len(service)}sB{len(protocol)}sB{len(domain_name)}sBHHIHHHHB{len(hostname)}sB{len(domain_name)}sB",
        *rservice_components, rtype, rclass, ttl, data_length, priority, weight, port, *rtarget_components)


# type TXT
def formatTypeTXT(name, ttl, txt_record_list):
    # hostname => label_length, label, [.,.,.], (0 sau compr pointer)
    # type TXT => 16
    # rclass => cache_flush + 0x0001
    # ttl
    # data length ( whole txt )
    # pt fiec record din txt
    # txt len:
    # txt:
    # [....]
    # name_compression_pointer = int("1100000000000000", 2)  # wtf is this (don't need it)

    # name ar fi de forma scanner1._udp.local dar am folosit doar scanner1.local din simplitatea crearii mesajului
    hostname, domain_name = name.split(".")
    rname_components = createLabels(name)

    # type TXT => 16
    rtype = 16

    # always flush the cache
    cache_flush_bit = 1
    rclass = int(f"{cache_flush_bit}000000000000001", 2)

    data_length = 0
    format = f"!B{len(hostname)}sB{len(domain_name)}sBHHIH"
    txt_components = []

    # format the txt list
    for record in txt_record_list:
        txt_len = len(record)

        data_length += txt_len + 1
        format += f"B{txt_len}s"

        txt_components.append(txt_len)
        txt_components.append(record.encode(FORMAT))

    return struct.pack(format, *rname_components, rtype, rclass, ttl, data_length, *txt_components)


# complex answer made of A + TXT + SRV msg-s
def createComplexResponse(service_name, target, ttl, port, ip, txt_list):
    header = format_MDNS_Header(1, 0, 3)

    answer0 = formatTypeA(target, ip, ttl)
    answer1 = formatTypeTXT(target, ttl, txt_list)
    answer2 = formatTypeSRV(service_name, target, port, ttl)

    return header + answer0 + answer1 + answer2


# unpack SRV msg
def unpackTypeSRV(response, offset):
    # unpack each field, incrementing the offset to make the unpacking easier
    rservice, offset = unpackName(response, offset)

    rtype = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    rclass = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    ttl = struct.unpack_from("!I", response, offset)[0]
    offset += 4

    data_length = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    priority = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    weight = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    port = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    rtarget, offset = unpackName(response, offset)
    offset += 1

    return (rtarget, rservice, ttl, port), offset


# unpack A msg
def unpackTypeA(response, offset):
    # unpack each field, incrementing the offset to make the unpacking easier
    rname, offset = unpackName(response, offset)

    rtype = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    rclass = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    ttl = struct.unpack_from("!I", response, offset)[0]
    offset += 4

    ip_length = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    ip = []
    while ip_length:
        ip_part = struct.unpack_from("!B", response, offset)[0]
        ip.append(str(ip_part))
        offset += 1
        ip_length -= 1
    ip = ".".join(ip)

    return (rname, rtype, rclass, ttl, ip), offset


# unpack TXT msg
def unpackTypeTXT(response, offset):
    # unpack each field, incrementing the offset to make the unpacking easier
    rname, offset = unpackName(response, offset)

    rtype = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    rclass = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    ttl = struct.unpack_from("!I", response, offset)[0]
    offset += 4

    data_length = struct.unpack_from("!H", response, offset)[0]
    offset += 2

    txt_record_list = []
    while data_length:
        record_len = struct.unpack_from("!B", response, offset)[0]
        offset += 1
        record = struct.unpack_from(f"!{record_len}s", response, offset)[0]
        offset += record_len

        txt_record_list.append(record.decode(FORMAT))

        data_length -= (record_len + 1)

    return (rname, rtype, ttl, txt_record_list), offset


# parse complex response
def parseComplexResponse(response):
    flags, _, an_count = unpackHeader(response)
    if not an_count == 3:
        return

    # start after the header ( = 12 bytes)
    offset = 12
    typeA_message, offset = unpackTypeA(response, offset)
    typeTXT_message, offset = unpackTypeTXT(response, offset)
    typeSRV_message, offset = unpackTypeSRV(response, offset)

    return typeA_message, typeTXT_message, typeSRV_message


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == "__main__":
    # tests

    # merge
    # request = createRequest("scanner1._scanner._udp.local", 0, "SRV")
    # print(request)
    # print(parseRequest(request))

    # merge
    # response = createResponse_TypePTR("scanner1._udp.local", "_scanner", 120)
    # print(response)
    # received = parsePTR_Response(response)
    # print(received)

    # merge
    # request = createResponse_TypeA("scanner1.local", "192.168.20.25", 120)
    # print(request)
    # print(unpackTypeA(request))

    # resp = createComplexResponse("_scanner._udp.local", "scanner1.local", 120, 5353, "192.168.20.25", txt)
    # print(resp)
    # parseComplexResponse(resp)

    # request = createRequest("scanner1._udp.local", 0, 'ptr')
    # print(request)
    # print(parseRequest(request))

    # query = "_scanner._udp.local"
    # print(".".join(query.split('.')[:-2]))

    pass
