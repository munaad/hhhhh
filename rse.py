# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 09:56:23 2024

@author: hmuaa
"""

import paramiko

def ssh_connect_and_configure(host, username, password, new_hostname):
    try:
        print("Connecting to device via SSH...")
        
        # Create an SSH client instance
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the device
        ssh_client.connect(host, username=username, password=password)
        print("Connected successfully!")
        
        # Start an interactive shell session
        shell = ssh_client.invoke_shell()

        # Send commands to configure the device
        shell.send("enable\n")
        shell.send(password + "\n")  # Send enable password
        shell.send("conf t\n")
        shell.send(f"hostname {new_hostname}\n")
        shell.send("end\n")
        
        # Retrieve the running configuration
        shell.send("show running-config\n")
        shell.send("exit\n")  # Exit the shell session

        # Allow time for output to be received
        shell.settimeout(1)
        running_config_output = ""
        while True:
            try:
                running_config_output += shell.recv(1024).decode('ascii')
            except paramiko.ssh_exception.SSHException:
                break  # Stop receiving if there's a timeout

        # Save the running configuration output to a file
        with open("running_config.txt", "w") as file:
            file.write(running_config_output)
        
        print("Configuration changed successfully and saved to 'running_config.txt'.")

        # Check configuration for hardening compliance
        hardening_checks(running_config_output)
    
    except Exception as e:
        print(f"An issue has occurred: {e}")
    finally:
        # Close the connection
        ssh_client.close()

def hardening_checks(config_output):
    print("\nChecking device hardening compliance...")

    # Simple Cisco hardening guidelines to check
    checks = {
        "no ip http server": "HTTP server should be disabled",
        "service password-encryption": "Service password encryption should be enabled",
        "no cdp run": "Cisco Discovery Protocol (CDP) should be disabled on Internet-facing interfaces",
        "enable secret": "Enable secret password should be set (not just 'enable password')",
        "banner login": "A login banner should be configured"
    }

    compliance_results = {}
    for command, advice in checks.items():
        compliance_results[command] = command in config_output

    # Display results
    for command, is_compliant in compliance_results.items():
        if is_compliant:
            print(f"PASS: {command} is set. ({checks[command]})")
        else:
            print(f"FAIL: {command} is NOT set. ({checks[command]})")

# Configuration parameters
host = "192.168.1.1"
username = "Muaad"
password = "bobwashere"
new_hostname = "Myrouter"

if __name__ == "__main__":
    ssh_connect_and_configure(host, username, password, new_hostname)

