#!/usr/bin/python3
import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
import threading
import socket
from Cache import *
from CacheRecord import *
from FormatWorker import *
import SRV

PORT = 5353
IP_ADDR = "224.0.0.251"
M_GROUP_ADDR = (IP_ADDR, PORT)
HEADER_SIZE = 64      # this should change if messages get long!
FORMAT = "utf-8"

browser = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
browser.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# browser.bind(("", PORT))
#
# m_req = struct.pack("4sl", socket.inet_aton(IP_ADDR), socket.INADDR_ANY)
# browser.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, m_req)

#           #         #       second socket options           #           #           #           #
browser_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
browser_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    browser_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except AttributeError:
    pass
browser_listener.bind(("", PORT))

m_req = struct.pack("4sl", socket.inet_aton(IP_ADDR), socket.INADDR_ANY)
browser_listener.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, m_req)
#


class RcpUiApp:
    def __init__(self, master=None):
        self.listener_is_active = False
        self.cache = Cache()

        # build ui
        self.app_top_level = tk.Tk() if master is None else tk.Toplevel(master)
        self.app_top_level.configure(background="#6b6b7e")
        self.app_top_level.geometry("600x600")
        self.app_top_level.resizable(False, False)
        self.up_frame = tk.Frame(self.app_top_level)
        self.up_frame.configure(background="#6b6b7e", height=200, width=600)
        self.title_frame = tk.Frame(self.up_frame)
        self.title_frame.configure(background="#6b6b7e", height=100, width=600)
        self.app_title_label = tk.Label(self.title_frame)
        self.app_title_label_text = tk.StringVar(value='Browse Services')
        self.app_title_label.configure(
            background="#6b6b7e",
            font="{Calibri} 24 {bold}",
            foreground="white",
            relief="raised",
            text='Browse Services',
            textvariable=self.app_title_label_text,
            width=25)
        self.app_title_label.grid(column=0, pady=30, row=0)
        self.title_frame.grid(column=0, row=0)
        self.search_bar_frame = tk.Frame(self.up_frame)
        self.search_bar_frame.configure(
            background="#6b6b7e", height=100, width=600)
        self.service_name_entry = tk.Entry(self.search_bar_frame)
        self.srv_search_var = tk.StringVar(value='search services...')
        self.service_name_entry.configure(
            font="{Calibri} 14 {}",
            foreground="black",
            justify="center",
            textvariable=self.srv_search_var,
            width=35)
        _text_ = 'search services...'
        self.service_name_entry.delete("0", "end")
        self.service_name_entry.insert("0", _text_)
        self.service_name_entry.grid(column=0, ipady=2, pady=13, row=0)
        self.search_btn = tk.Button(self.search_bar_frame)
        self.search_btn.configure(
            anchor="center",
            background="#6b6b7e",
            font="{Calibri} 11 {}",
            foreground="white",
            overrelief="raised",
            relief="groove",
            text='Search',
            width=10)
        self.search_btn.grid(column=1, padx=5, row=0)
        self.search_btn.configure(command=self.search_service)
        self.search_bar_frame.grid(column=0, row=1)
        self.up_frame.grid(column=0, row=0)
        self.results_frame = tk.Frame(self.app_top_level)
        self.results_frame.configure(
            background="#6b6b7e", height=400, width=600)
        self.available_srv_frame = tk.Frame(self.results_frame)
        self.available_srv_frame.configure(background="#6b6b7e", width=250)
        self.services_label_frame = tk.Frame(self.available_srv_frame)
        self.services_label_frame.configure(
            background="#6b6b7e", borderwidth=1, height=25, width=250)
        self.available_services_label = ttk.Label(self.services_label_frame)
        self.available_services_label.configure(
            anchor="n",
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            text='Available Services',
            width=20)
        self.available_services_label.grid(column=0, row=0)
        self.services_label_frame.grid(column=0, pady=15, row=0)
        self.services_label_frame.grid_propagate(False)
        self.services_label_frame.grid_anchor("n")
        self.services_list_frame = tk.Frame(self.available_srv_frame)
        self.services_list_frame.configure(
            background="#6b6b7e", height=375, width=250)
        self.services_listbox = tk.Listbox(self.services_list_frame)
        self.services_listbox.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            height=12,
            selectmode="single",
            width=28)
        self.services_listbox.grid(column=0, padx=10, pady=15, row=0)
        select_btn = tk.Button(self.services_list_frame)
        select_btn.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            overrelief="raised",
            relief="groove",
            text='Select',
            width=10)
        select_btn.grid(column=0, pady=25, row=1)
        select_btn.configure(command=self.select_service)
        self.services_list_frame.grid(column=0, row=1)
        self.services_list_frame.grid_propagate(False)          # was 0
        self.services_list_frame.grid_anchor("n")
        separator_1 = ttk.Separator(self.available_srv_frame)
        separator_1.configure(orient="horizontal")
        separator_1.grid(column=0, row=0, sticky="sew")
        self.available_srv_frame.grid(column=0, row=0, sticky="ns")
        self.available_srv_frame.grid_propagate(False)
        self.available_srv_frame.grid_anchor("n")
        self.srv_txt_frame = tk.Frame(self.results_frame)
        self.srv_txt_frame.configure(
            background="#6b6b7e", height=435, width=348)
        self.srv_txt_record_label = tk.Label(self.srv_txt_frame)
        self.srv_txt_record_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            text='TXT Record')
        self.srv_txt_record_label.grid(column=0, pady=2, row=0)
        self.srv_txt_record = ScrolledText(self.srv_txt_frame)
        self.srv_txt_record.configure(
            font="{Calibri} 12 {}",
            foreground="black",
            height=6,
            relief="flat",
            spacing1=5,
            width=35,
            wrap="word")
        _text_ = 'info \nkey=value\n...'
        self.srv_txt_record.insert("0.0", _text_)
        self.srv_txt_record.grid(pady=10, row=1)
        self.browser_local_cache = ScrolledText(self.srv_txt_frame)
        self.browser_local_cache.configure(
            font="{Calibri} 12 {}",
            foreground="black",
            height=6,
            relief="flat",
            spacing1=5,
            width=35,
            wrap="word")
        _text_ = 'info \nkey=value\n...'
        self.browser_local_cache.insert("0.0", _text_)
        self.browser_local_cache.grid(pady=10, row=3)
        self.browser_local_cache_label = tk.Label(self.srv_txt_frame)
        self.browser_local_cache_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            text='Local Cache')
        self.browser_local_cache_label.grid(
            column=0, pady=2, row=2, sticky="new")
        separator_2 = ttk.Separator(self.srv_txt_frame)
        separator_2.configure(orient="horizontal")
        separator_2.grid(column=0, row=1, sticky="new")
        separator_4 = ttk.Separator(self.srv_txt_frame)
        separator_4.configure(orient="horizontal")
        separator_4.grid(column=0, row=2, sticky="sew")
        self.srv_txt_frame.grid(column=2, row=0)
        self.srv_txt_frame.grid_propagate(False)
        self.srv_txt_frame.grid_anchor("n")
        separator_3 = ttk.Separator(self.results_frame)
        separator_3.configure(orient="vertical")
        separator_3.grid(column=1, row=0, sticky="nse")
        self.results_frame.grid(column=0, row=1)
        separator_5 = ttk.Separator(self.app_top_level)
        separator_5.configure(orient="horizontal")
        separator_5.grid(column=0, row=0, sticky="sew")

        # Main widget
        self.mainwindow = self.app_top_level

    def updateCacheWindow(self):
        now = time.time()
        self.browser_local_cache.delete("0.0", "end")
        for cache_record in self.cache.getCache():
            default_ttl = cache_record.getDefaultTTL()
            time_created = cache_record.getTimeCreated()
            time_passed = now - time_created

            if math.floor(default_ttl - time_passed) > 0:
                cache_record.setTTL(math.floor(default_ttl - time_passed))
                self.browser_local_cache.insert(tk.INSERT, str(cache_record) + "\n")

    def updateTXTRecordWindow(self, text_record_content):
        self.srv_txt_record.delete("0.0", "end")
        for record in text_record_content:
            self.srv_txt_record.insert(tk.INSERT, record + "\n")

    def response_worker(self):
        print("[Waiting for responses..]")
        while True:
            response, recv_from = browser.recvfrom(1024)

            # unpack header
            flags, qd_count, an_count = unpackHeader(response)

            # check an_count
            if an_count == 1:
                # if 1 => a/ptr response
                rname, rtype, rclass, ttl, data = parseSimpleResponse(response)
                if rtype == 12:
                    # ptr
                    ptr_serv = ""
                    if data:
                        ptr_serv = data.split(".")[1]
                    instance = ".".join(rname.split(".")[:-2])
                    if ptr_serv:
                        self.services_listbox.insert(1, f"{instance}.{ptr_serv}")
                    else:
                        self.services_listbox.insert(1, f"{instance}")

                elif rtype == 1:
                    # a
                    # received change configs msg
                    print(response)
                    browser.sendto("received".encode(FORMAT), recv_from)
                    # here we receive a response regarding any changes that have been made upon a device
                    # ... (not working)

            elif an_count == 3:
                # if 3 => srv + a + txt req
                typeA_message, typeTXT_message, typeSRV_message = parseComplexResponse(response)

                # type A
                hostname = ".".join(typeA_message[0].split(".")[:-1])
                rclass = typeA_message[2]
                ttl = typeA_message[3]
                ip = typeA_message[4]

                # type TXT
                txt_rec = typeTXT_message[3]

                # type SRV
                srv = typeSRV_message[1].split(".")[0]

                # cache flush
                if rclass != 1:
                    # store record and update cache
                    cache_record = CacheRecord(f"{hostname}", ip, ttl)
                    self.cache.flushCacheRecord(cache_record)
                else:
                    # should not get here
                    pass

                # show txt rec
                self.updateCacheWindow()
                self.updateTXTRecordWindow(txt_rec)

    def listenToResponses(self):
        listen_thread = threading.Thread(target=self.response_worker)
        listen_thread.start()

    def logs_listener(self):
        while True:
            response, recv_from = browser_listener.recvfrom(1024)
            flags, qd_count, an_count = unpackHeader(response)

            if flags and an_count == 1:
                # single response
                rname, rtype, rclass, ttl, data = parseSimpleResponse(response)
                if rtype == 1 and rclass != 1:
                    # type A, cache flush
                    hostname = rname.split(".")[0]
                    cache_record = CacheRecord(hostname, data, ttl)
                    self.cache.updateCacheRecord(cache_record)
                    self.updateCacheWindow()

    def listenToChangeLogs(self):
        listen_thread = threading.Thread(target=self.logs_listener)
        listen_thread.start()

    def run(self):
        self.listenToChangeLogs()
        self.mainwindow.mainloop()

    def search_service(self):
        self.updateCacheWindow()
        service = self.service_name_entry.get()
        isEmpty = 1 if service == "" else 0
        self.services_listbox.delete(0, tk.END)

        if isEmpty:
            service = '_services._dns-sd._udp.local'
        else:
            # re-format for searching services => user can only search for the actual name of the service
            if not service.startswith("_"):
                service = f"_{service}"
            if not service.endswith("_udp.local"):
                service = f"{service}._udp.local"

        # send parsed data to group
        request = createRequest(service, 0, "ptr")
        browser.sendto(request, M_GROUP_ADDR)

        if not self.listener_is_active:
            self.listener_is_active = True
            self.listenToResponses()

    def select_service(self):
        if self.listener_is_active:
            selected_instance = self.services_listbox.get(self.services_listbox.curselection()[0])
            qname = f"{selected_instance}._udp.local"

            request = createRequest(qname, 0, 'srv')

            ip_from_cache = self.cache.searchCacheByHostname(selected_instance.split(".")[0])
            if ip_from_cache:
                print("Sent to the ip from cache!\n")
                browser.sendto(request, (ip_from_cache, PORT))

            browser.sendto(request, M_GROUP_ADDR)


if __name__ == "__main__":
    app = RcpUiApp()
    app.run()