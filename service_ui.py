#!/usr/bin/python3
import random
import socket
import threading
import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText

from SRV import *
from A import *
from TXT import *
from FormatWorker import *

service_types = ["printer", "tv", "camera", "speaker"]
PORT = 5353
IP_ADDR = "224.0.0.251"
M_GROUP_ADDR = (IP_ADDR, PORT)
HEADER_SIZE = 64      # this should change if messages get long!
FORMAT = "utf-8"

#           #         #        socket options           #           #           #           #
service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
service.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    service.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except AttributeError:
    pass
service.bind(("", PORT))

m_req = struct.pack("4sl", socket.inet_aton(IP_ADDR), socket.INADDR_ANY)
service.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, m_req)
#           #               #               #                   #               #               #


class RCPServiceApp:
    def __init__(self, master=None):
        # Variables
        self.default_service_name = service_types[random.randint(0, len(service_types) - 1)]
        self.default_hostname = self.default_service_name + str(random.randint(1, 15))  # instance name
        self.default_ip = f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        self.configs_changed = False

        # Records
        # Initialization of records is always going to pass the validations
        self.A_RECORD = A_RECORD(self.default_hostname, self.default_ip)
        self.SRV_RECORD = SRV_RECORD(self.default_service_name, self.A_RECORD.getHostname())
        self.TXT_RECORD = TXT_RECORD()

        # build ui
        toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        toplevel1.configure(background="#6b6b7e", height=600, width=600)
        toplevel1.resizable(False, False)
        self.context_frame = tk.Frame(toplevel1)
        self.context_frame.configure(
            background="#6b6b7e", height=600, width=600)
        self.hostname_entry = tk.Entry(self.context_frame)
        self.hostname = tk.StringVar(value='Hostname')
        self.hostname_entry.configure(
            font="{Calibri} 12 {}",
            justify="center",
            relief="groove",
            textvariable=self.hostname,
            width=30)
        _text_ = self.A_RECORD.getHostname()  # change default hostname value here
        self.hostname_entry.delete("0", "end")
        self.hostname_entry.insert("0", _text_)
        self.hostname_entry.place(
            anchor="center",
            relx=0.5,
            rely=0.265,
            width=260,
            x=0,
            y=0)
        self.ip_entry = tk.Entry(self.context_frame)
        self.ip = tk.StringVar(value='IP')
        self.ip_entry.configure(
            font="{Calibri} 12 {}",
            justify="center",
            relief="groove",
            textvariable=self.ip,
            width=30)
        _text_ = self.A_RECORD.getIP()          # change default ip value here
        self.ip_entry.delete("0", "end")
        self.ip_entry.insert("0", _text_)
        self.ip_entry.place(
            anchor="center",
            relx=0.5,
            rely=0.35,
            width=260,
            x=0,
            y=0)
        self.text_record = ScrolledText(self.context_frame)
        self.text_record.configure(
            font="{Calibri} 12 {}",
            height=10,
            relief="groove",
            width=30)
        _text_ = str(self.TXT_RECORD)  # change default text-record value here
        self.text_record.insert("0.0", _text_)
        self.text_record.place(anchor="center", relx=0.5, rely=0.68, x=0, y=0)
        self.save_btn = tk.Button(self.context_frame)
        self.save_button = tk.StringVar(value='Save')
        self.save_btn.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            overrelief="raised",
            relief="groove",
            text='Save',
            textvariable=self.save_button,
            width=36)
        self.save_btn.place(
            anchor="center",
            height=30,
            relx=0.5,
            rely=0.92,
            width=260,
            x=0,
            y=0)
        self.save_btn.configure(command=self.save_config)
        self.separator_1 = ttk.Separator(self.context_frame)
        self.separator_1.configure(orient="vertical")
        self.separator_1.place(
            anchor="center",
            relx=0.5,
            rely=0.48,
            width=450,
            x=0,
            y=0)
        self.separator_2 = ttk.Separator(self.context_frame)
        self.separator_2.configure(orient="vertical")
        self.separator_2.place(
            anchor="center",
            relx=0.5,
            rely=0.87,
            width=450,
            x=0,
            y=0)
        self.title_label = tk.Label(self.context_frame)
        self.title_label.configure(
            background="#6b6b7e",
            font="{Calibri} 24 {}",
            foreground="#ffffff",
            relief="raised",
            text='Service Manager',
            width=16)
        self.title_label.place(anchor="center", relx=0.5, rely=0.05, x=0, y=0)
        self.separator_3 = ttk.Separator(self.context_frame)
        self.separator_3.configure(orient="vertical")
        self.separator_3.place(
            anchor="center",
            relx=0.5,
            rely=0.11,
            width=450,
            x=0,
            y=5)
        self.service_type_entry = tk.Entry(self.context_frame)
        self.service_type = tk.StringVar(value='Service Type')
        self.service_type_entry.configure(
            font="{Calibri} 12 {}",
            justify="center",
            relief="groove",
            textvariable=self.service_type,
            width=30)
        _text_ = self.SRV_RECORD.getService()[1:]  # change default service-type value here
        self.service_type_entry.delete("0", "end")
        self.service_type_entry.insert("0", _text_)
        self.service_type_entry.place(
            anchor="center",
            relx=0.5,
            rely=0.18,
            width=260,
            x=0,
            y=0)
        self.srv_label = tk.Label(self.context_frame)
        self.srv_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            justify="center",
            relief="sunken",
            text='SRV_TYPE',
            width=10)
        self.srv_label.place(relx=0.09, rely=0.16, x=0, y=0)
        self.hostname_label = tk.Label(self.context_frame)
        self.hostname_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            justify="center",
            relief="sunken",
            text='HOSTNAME',
            width=10)
        self.hostname_label.place(relx=0.09, rely=0.245, x=0, y=0)
        self.ip_label = tk.Label(self.context_frame)
        self.ip_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            justify="center",
            relief="sunken",
            text='IP',
            width=10)
        self.ip_label.place(relx=0.09, rely=0.33, x=0, y=0)
        self.txt_record_label = tk.Label(self.context_frame)
        self.txt_record_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            justify="center",
            relief="sunken",
            text='TXT_RECORD',
            width=13)
        self.txt_record_label.place(relx=0.06, rely=0.58, x=0, y=0)
        self.ttl_entry = tk.Entry(self.context_frame)
        self.ttl = tk.StringVar(value='TTL')
        self.ttl_entry.configure(
            font="{Calibri} 12 {}",
            justify="center",
            relief="groove",
            textvariable=self.ttl,
            width=30)
        _text_ = self.SRV_RECORD.getTTL()
        self.ttl_entry.delete("0", "end")
        self.ttl_entry.insert("0", _text_)
        self.ttl_entry.place(
            anchor="center",
            relx=0.5,
            rely=0.43,
            width=260,
            x=0,
            y=0)
        self.ttl_entry_label = tk.Label(self.context_frame)
        self.ttl_entry_label.configure(
            background="#6b6b7e",
            font="{Calibri} 12 {}",
            foreground="white",
            justify="center",
            relief="sunken",
            text='TTL',
            width=10)
        self.ttl_entry_label.place(relx=0.09, rely=0.41, x=0, y=0)
        self.context_frame.place(anchor="nw", x=0, y=0)

        # Main widget
        self.mainwindow = toplevel1

    def requests_listener_worker(self):
        while True:
            request, received_from = service.recvfrom(1024)
            flags, qd_count, _, query, qtype = parseRequest(request)

            if flags != 0:
                pass
            elif not qd_count:
                pass
            elif not query.endswith("_udp.local"):
                pass
            else:
                if qtype == 12:
                    # ptr request
                    check_srv = ".".join(query.split('.')[:-2])
                    if check_srv == self.SRV_RECORD.getService() or check_srv == "_services._dns-sd":
                        # hostname, service, ttl
                        hostname = f"{self.A_RECORD.getHostname()}.{self.SRV_RECORD.getProto()}.{self.SRV_RECORD.getDomain()}"
                        response = createResponse_TypePTR(hostname, self.SRV_RECORD.getService(), self.SRV_RECORD.getTTL())

                        service.sendto(response, received_from)

                elif qtype == 33:
                    # srv request
                    check_host = ".".join(query.split('.')[:-2])
                    if check_host == f"{self.A_RECORD.getHostname()}.{self.SRV_RECORD.getService()}":
                        # service, target, ttl, port, ip, txt_record
                        srv = f"{self.SRV_RECORD.getService()}.{self.SRV_RECORD.getProto()}.{self.SRV_RECORD.getDomain()}"
                        target = f"{self.A_RECORD.getHostname()}.{self.SRV_RECORD.getDomain()}"
                        response = createComplexResponse(srv, target, self.SRV_RECORD.getTTL(), PORT, self.A_RECORD.getIP(), self.TXT_RECORD.getList())
                        service.sendto(response, received_from)
                else:
                    pass

    def listenToRequests(self):
        listen_thread = threading.Thread(target=self.requests_listener_worker)
        listen_thread.start()

    def run(self):
        # verificari
        # print("SRV: ", self.SRV_RECORD)
        # print("A: ", self.A_RECORD)
        # print("TXT: ", self.TXT_RECORD.getList())

        self.listenToRequests()
        self.mainwindow.mainloop()

    def save_config(self):
        self.A_RECORD.setHostname(self.hostname.get())
        flagA, msgA = self.A_RECORD.setIP(self.ip.get())

        flagTTL, msgTTL = self.SRV_RECORD.setTTL(self.ttl_entry.get())

        self.SRV_RECORD.setService(self.service_type.get())
        self.SRV_RECORD.setTarget(self.A_RECORD.getHostname())

        flagT, msgT = self.TXT_RECORD.updateList(self.text_record.get("0.0", "end").split("\n"))

        if not flagA or not flagT or not flagTTL:
            self.ip.set(self.A_RECORD.getIP())
            self.text_record.delete("0.0", "end")
            self.text_record.insert(tk.INSERT, str(self.TXT_RECORD))

            info_message = msgA + msgT + msgTTL
            tkinter.messagebox.showerror("Warning", info_message + "\nYour configs were not saved!")
        else:
            tkinter.messagebox.showinfo("Success", "Saved your configs..")
            # self.configs_changed = True

            # send request to flush the cache and to store changes
            hostname = f"{self.hostname.get()}.{self.SRV_RECORD.getDomain()}"

            # create change log to send to the multicast group
            change_configs_response = createResponse_TypeA(hostname, self.ip.get(), int(self.ttl_entry.get()))
            service.sendto(change_configs_response, M_GROUP_ADDR)


        # verificari
        # print("SRV: ", self.SRV_RECORD)
        # print("A: ", self.A_RECORD)
        # print("TXT: ", self.TXT_RECORD.getList())


if __name__ == "__main__":
    app = RCPServiceApp()
    app.run()
