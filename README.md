# MDNS Project

## Description

This is a Python application designed to facilitate service discovery within local networks. Leveraging MDNS (Multicast DNS) and DNS-SD (DNS Service Discovery) protocols, it provides a seamless mechanism for identifying and accessing available services. The application operates over UDP (User Datagram Protocol), ensuring lightweight communication suitable for real-time discovery scenarios. Packet structures are crafted to be identifiable using Wireshark, simplifying testing and analysis. The implementation adheres closely to relevant RFC documents, ensuring compliance and interoperability with existing networking standards.

## Algorithms Used

- **MDNS (Multicast DNS)**: Enables the resolution of hostnames and service discovery within the local network without relying on a centralized DNS server. By broadcasting queries and responses to a multicast group, devices can efficiently discover services offered by other devices on the same network segment.
- **DNS-SD (DNS Service Discovery)**: Allows clients to browse and discover services advertised within specified domains. This mechanism utilizes DNS queries and responses to locate services based on service type, name, and other attributes, making it suitable for discovering a wide range of networked services.
- **UDP (User Datagram Protocol)**: Chosen for its simplicity and efficiency in communication. Unlike TCP, UDP does not establish a persistent connection, making it well-suited for scenarios where real-time data transmission is crucial, such as service discovery.
- **Packet Structure**: Each UDP packet follows a specific structure comprising headers and payload. The headers contain essential information such as source and destination ports, packet length, and checksum for error detection. The payload contains the actual data being transmitted, formatted according to the MDNS and DNS-SD specifications for service discovery.
- **Wireshark Identification**: Packet structures are designed to be identifiable using Wireshark, a popular network protocol analyzer. This ensures that developers can easily inspect and analyze the packets exchanged during service discovery, facilitating debugging and optimization efforts.

## Browser-Service Architecture

- **Browser Interface**: The browser component of the application provides a user-friendly interface for searching and discovering services available within the local network. Users can initiate searches and view the list of discovered services, along with relevant information such as service type, name, and network location.
- **Service Functionality**: Each discovered service adheres to a predefined functionality, responding to browser calls for establishing connections and other purposes. When a user selects a service from the browser interface, the application initiates a connection request to the selected service. Upon successful connection establishment, the service responds to subsequent requests from the browser, providing access to its functionalities and resources as defined.
- **Connection Establishment**: The browser initiates a connection establishment process with the selected service, typically involving handshake protocols to negotiate connection parameters and ensure compatibility between the browser and the service. Once the connection is established, the browser can interact with the service to access its features and data.

![Image](images\img1.png)
![Image](images\img2.png)
