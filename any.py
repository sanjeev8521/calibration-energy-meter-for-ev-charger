import asyncio
import tkinter as tk
from tkinter import ttk
from bleak import BleakClient, BleakScanner
import struct
import binascii
char_uuid = "49535343-1e4d-4bd9-ba61-23c647249616"
DATA = None


def callback(sender, data):
    global DATA
    print(
        f"Sender is: {sender}: Data Received is: {binascii.hexlify(data).decode()}")
    DATA = data
    app.update_received_data()
    app.convert_and_display_float()
    app.calculate_and_display_result()


async def send_command_and_receive_data(address, cmd):
    global DATA
    async with BleakClient(address) as client:
        await client.start_notify(char_uuid, callback)
        await client.write_gatt_char(char_uuid, bytearray.fromhex(cmd), response=True)
        await asyncio.sleep(5)
        await client.stop_notify(char_uuid)
        return binascii.hexlify(DATA).decode()


class BluetoothApp:
    def __init__(self, root):
        self.root = root
        self.root.title("sanjeev pandey")
        self.root.geometry("800x600")
        self.root.configure(bg="red")
        self.devices = []
        self.device_tree = ttk.Treeview(root, columns=(
            "Name", "MAC Address"), show="headings")
        self.device_tree.heading("Name", text="Name")
        self.device_tree.heading("MAC Address", text="MAC Address")
        self.device_tree.pack()
        self.scan_button = tk.Button(
            root, text="Scan Devices", bg="green", command=self.discover_devices)
        self.scan_button.pack()
        self.pair_button = tk.Button(
            root, text="Pair Device", bg="green", command=self.pair_device)
        self.pair_button.pack()
        self.selected_device_address = None
        self.voltage_label = tk.Label(root, text="Enter Voltage:", bg="yellow")
        self.voltage_label.pack()
        self.voltage_entry = tk.Entry(root)
        self.voltage_entry.pack()
        self.send_button = tk.Button(
            root, text="Send Command", bg="green", command=self.send_command)
        self.send_button.pack()
        self.command_label = tk.Label(root, text="Enter Command:", bg="yellow")
        self.command_label.pack()
        self.command_entry = tk.Entry(root)
        self.command_entry.pack()
        self.send_custom_command_button = tk.Button(
            root, text="Send Custom Command", bg="green", command=self.send_custom_command)
        self.send_custom_command_button.pack()
        self.float_label = tk.Label(
            root, text="Received Data (Float):", bg="blue")
        self.float_label.pack()
        self.float_display = tk.Entry(root, state="readonly")
        self.float_display.pack()
        self.decimal_label = tk.Label(root, bg="blue")
        self.decimal_label.pack()
        self.decimal_display = tk.Entry(root, state="readonly")
        self.decimal_display.pack()
        self.hex_label = tk.Label(root, text="Received Data (Hex):", bg="blue")
        self.hex_label.pack()
        self.hex_display = tk.Entry(root, state="readonly")
        self.hex_display.pack()
        self.last8_decimal_label = tk.Label(root, bg="blue")
        self.last8_decimal_label.pack()
        self.last8_decimal_display = tk.Entry(root, state="readonly")
        self.last8_decimal_display.pack()
        self.new_data_label = tk.Label(root, text="", bg="blue")
        self.new_data_label.pack()
        self.new_data_display = tk.Entry(root, state="readonly")
        self.new_data_display.pack()
        self.new_data_hex_label = tk.Label(
            root, text="New Data (Hex):", bg="blue")
        self.new_data_hex_label.pack()
        self.new_data_hex_display = tk.Entry(root, state="readonly")
        self.new_data_hex_display.pack()
        self.result_label = tk.Label(
            root, text="Result (Entered Voltage / Received Float Value):", bg="blue")
        # self.result_label.pack()
        self.result_display = tk.Entry(root, state="readonly", bg="blue")
        self.result_display.pack()
        self.result_decimal_label = tk.Label(root, text="", bg="blue")
        self.result_decimal_label.pack()
        self.result_decimal_display = tk.Entry(
            root, state="readonly", bg="blue")
        self.result_decimal_display.pack()
        self.hide_last8_digits_decimal()

    def hide_last8_digits_decimal(self):
        self.last8_decimal_label.pack_forget()
        self.last8_decimal_display.pack_forget()

    def pair_device(self):
        selected_item = self.device_tree.selection()
        if selected_item:
            device_name = self.device_tree.item(selected_item, "values")[0]
            device_address = self.device_tree.item(selected_item, "values")[1]
            self.selected_device_address = device_address
            self.hide_received_data_box()
            self.hide_last8_digits_decimal()
            self.hide_status_box()
            is_reachable = asyncio.run(
                self.check_device_reachability(device_address))
            if is_reachable:
                self.show_received_data_box()
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(
                    tk.END, f"Device {device_name} ({device_address}) is reachable and accepted the request.")
            else:
                self.hide_received_data_box()
                self.hide_last8_digits_decimal()
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(
                    tk.END, f"Device {device_name} ({device_address}) is not reachable or did not accept the request.")

    async def check_device_reachability(self, device_address):
        try:
            async with BleakClient(device_address) as client:
                return True
        except Exception as e:
            print(f"Error checking device reachability: {e}")
            return False

    def show_received_data_box(self):
        self.float_label.pack()
        # self.float_display.pack()
        self.new_data_hex_display.pack()

    def hide_received_data_box(self):
        self.decimal_label.pack_forget()
        self.decimal_display.pack_forget()
        self.hex_label.pack_forget()
        self.hex_display.pack_forget()
        self.last8_decimal_label.pack_forget()
        self.last8_decimal_display.pack_forget()
        self.result_decimal_label.pack_forget()
        self.result_decimal_display.pack_forget()
        self.float_display.pack()

    def hide_status_box(self):
        pass

    def send_command(self):
        if self.selected_device_address:
            first_command = "10ac0a00"
            received_data = asyncio.run(send_command_and_receive_data(
                self.selected_device_address, first_command))
            self.convert_and_display_float()
            self.calculate_and_display_result()
            second_command = "10ac0400"
            received_data_hex = asyncio.run(send_command_and_receive_data(
                self.selected_device_address, second_command))
            self.update_received_hex_data()
            self.update_last8_decimal_data()
            self.update_new_data()
            self.update_new_data_hex()
            self.update_result_decimal_data()

    def send_custom_command(self):
        if self.selected_device_address:
            custom_command = self.command_entry.get()
            if custom_command:
                received_data = asyncio.run(send_command_and_receive_data(
                    self.selected_device_address, custom_command))
                self.update_received_hex_data()
                self.update_last8_decimal_data()
                self.update_new_data()
                self.update_new_data_hex()
                self.update_result_decimal_data()
            else:
                print("Please enter a custom command before sending.")

    def update_received_data(self):
        hex_data = binascii.hexlify(DATA).decode()
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, hex_data)

    def update_received_hex_data(self):
        hex_data = binascii.hexlify(DATA).decode()
        self.hex_display.config(state="normal")
        self.hex_display.delete(0, tk.END)
        self.hex_display.insert(0, hex_data)
        self.hex_display.config(state="readonly")

    def update_last8_decimal_data(self):
        hex_data = binascii.hexlify(DATA).decode()
        last_8_digits = hex_data[-8:]
        decimal_value = int(last_8_digits, 16)
        self.last8_decimal_display.config(state="normal")
        self.last8_decimal_display.delete(0, tk.END)
        self.last8_decimal_display.insert(0, f"{decimal_value}")
        self.last8_decimal_display.config(state="readonly")

    def update_new_data(self):
        hex_data = binascii.hexlify(DATA).decode()
        last_8_digits = hex_data[-8:]
        decimal_value = int(last_8_digits, 16)
        entered_voltage = float(self.voltage_entry.get())
        float_value = float(self.float_display.get())
        result = entered_voltage / float_value
        new_data = int(decimal_value * result)
        self.new_data_display.config(state="normal")
        self.new_data_display.delete(0, tk.END)
        self.new_data_display.insert(0, f"{new_data}")
        self.new_data_display.config(state="readonly")

    def update_new_data_hex(self):
        new_data = int(self.new_data_display.get())
        hex_data = hex(new_data)
        self.new_data_hex_display.config(state="normal")
        self.new_data_hex_display.delete(0, tk.END)
        self.new_data_hex_display.insert(0, hex_data)
        self.new_data_hex_display.config(state="readonly")

    def update_result_decimal_data(self):
        entered_voltage = float(self.voltage_entry.get())
        float_value = float(self.float_display.get())
        result = entered_voltage / float_value
        hex_data = binascii.hexlify(DATA).decode()
        last_8_digits = hex_data[-8:]
        decimal_value = int(last_8_digits, 16)
        result_decimal = decimal_value * result
        self.result_decimal_display.config(state="normal")
        self.result_decimal_display.delete(0, tk.END)
        self.result_decimal_display.insert(0, f"{result_decimal:.3f}")
        self.result_decimal_display.config(state="readonly")

    def convert_and_display_float(self):
        hex_data = binascii.hexlify(DATA).decode()
        last_8_digits = hex_data[-8:]
        float_value = struct.unpack('>f', bytes.fromhex(last_8_digits))[0]
        self.float_display.config(state="normal")
        self.float_display.delete(0, tk.END)
        self.float_display.insert(0, f"{float_value:.6f}")
        self.float_display.config(state="readonly")

    def convert_and_display_decimal(self):
        hex_data = binascii.hexlify(DATA).decode()
        decimal_value = int(hex_data, 16)
        self.decimal_display.config(state="normal")
        self.decimal_display.delete(0, tk.END)
        self.decimal_display.insert(0, f"{decimal_value}")
        self.decimal_display.config(state="readonly")

    def calculate_and_display_result(self):
        entered_voltage = self.voltage_entry.get()
        if entered_voltage:
            try:
                entered_voltage = float(entered_voltage)
                float_value = float(self.float_display.get())
                result = entered_voltage / float_value
                self.result_display.config(state="normal")
                self.result_display.delete(0, tk.END)
                self.result_display.insert(0, f"{result:.3f}")
                self.result_display.config(state="readonly")
            except ValueError:
                print("Invalid voltage value. Please enter a valid float.")

    def discover_devices(self):
        self.device_tree.delete(*self.device_tree.get_children())
        self.devices = []
        devices = asyncio.run(BleakScanner.discover())
        filtered_devices = self.filter_devices_by_criteria(devices)
        for device in filtered_devices:
            device_name = device.name if device.name else "Unknown"
            device_address = device.address
            self.device_tree.insert(
                "", tk.END, values=(device_name, device_address))
            self.devices.append(device)

    def filter_devices_by_criteria(self, devices):
        return [
            device for device in devices
            if device.name and device.address and
            len(device.name) >= 2 and len(device.address) >= 2 and
            device.name[-2:].lower() == device.address[-2:].lower()
        ]


if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothApp(root)
root.mainloop()
