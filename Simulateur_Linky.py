import serial
import time
import threading

# ---------------- CHECKSUM ----------------

def setCheckSum(data):
    checksum = 0
    for car in data:
        checksum += ord(car)
    checksum &= 0x3F
    checksum += 0x20
    return chr(checksum)

def build_line(line):
    return f"{line} {setCheckSum(line)}\r\n"

# ---------------- SIMULATEUR ----------------

class TeleinfoSimulator:
    def __init__(self, port, type, isousc):
        self.isousc = isousc
        self.iinst = 0
        self.hchp = 3676
        self.ptec = "HP.."
        self.running = True
        self.type = type

        self.ser = serial.Serial(
            port=port,
            baudrate=1200,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

    def build_frame(self):
        papp = self.iinst * 230
        self.hchp += 1
        
        frame = [
                "IMAX 090",
                "OPTARIF HC..",
                "HHPHC A",
                "BASE 002844816",
                "ADCO 022064215196",
                "HCHC 034366502",
                f"ISOUSC {self.isousc}",
                f"PTEC {self.ptec}",
                f"HCHP {self.hchp}",
                "MOTDETAT 000000"
            ]

        if self.type == "M":
            frame.append(f"IINST {self.iinst}")
        else:
            frame.append(f"IINST1 {self.iinst}")
            frame.append(f"IINST2 {self.iinst}")
            frame.append(f"IINST3 {self.iinst}")
            
        frame.append(f"PAPP {papp}")

        return frame

    def send_loop(self):
        print("Envoi de la trame toutes les secondes…")
        while self.running:
            for line in self.build_frame():
                self.ser.write(build_line(line).encode("ascii"))
                time.sleep(0.02)
            time.sleep(0.2)

    def input_loop(self):
        print("Valeur IINST :")
        while self.running:
            try:
                val = input("> IINST = XX or PTEC = HP.. / HC.. ")
                self.iinst = int(val)
                print(f"IINST mis à jour à {self.iinst} A")
            except ValueError:
                self.ptec = val
                print(f"PTEC mis à jour à {self.ptec}")

    def stop(self):
        self.running = False
        self.ser.close()

# ---------------- MAIN ----------------

def main():
    port = input("Port COM (ex: COM3 ou /dev/ttyUSB0) : ").strip()
    type = input("Type Linky (ex: M (Monophasé) ou T (Triphasé)) : ").strip()
    isousc = input("Valeur ISOUSC : ").strip()

    sim = TeleinfoSimulator(port, type, isousc)

    try:
        t_send = threading.Thread(target=sim.send_loop, daemon=True)
        t_input = threading.Thread(target=sim.input_loop, daemon=True)

        t_send.start()
        t_input.start()

        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nArrêt du simulateur")
        sim.stop()

if __name__ == "__main__":
    main()
