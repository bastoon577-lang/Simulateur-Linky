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
        self.ptec = "HP.."
        self.running = True
        self.type = type

        # Initialisation des index réels sous forme de Float à 0.0
        self.hchp_value = 0.0
        self.hchc_value = 0.0
        self.last_update_time = time.time()

        self.ser = serial.Serial(
            port=port,
            baudrate=1200,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

    def build_frame(self):
        if self.type == "M":
            papp = self.iinst * 230
        else:
            # En triphasé : Somme des 3 phases (IINST1 + IINST2 + IINST3) * 230V
            papp = (self.iinst + (self.iinst + 2) + (self.iinst + 3)) * 230
        
        # --- Calcul de l'énergie consommée ---
        now = time.time()
        elapsed_seconds = now - self.last_update_time
        self.last_update_time = now
        
        delta_wh = (papp * elapsed_seconds) / 3600.0
        
        if self.ptec == "HP..":
            self.hchp_value += delta_wh
        elif self.ptec == "HC..":
            self.hchc_value += delta_wh
            
        # Formatage sur 9 chiffres exigé par le Linky
        str_hchp = f"{int(self.hchp_value):09d}"
        str_hchc = f"{int(self.hchc_value):09d}"
        
        frame = [
                "IMAX 090",
                "OPTARIF HC..",
                "HHPHC A",
                "BASE 002844816",
                "ADCO 022064215196",
                f"HCHC {str_hchc}",
                f"ISOUSC {self.isousc}",
                f"PTEC {self.ptec}",
                f"HCHP {str_hchp}",
                "MOTDETAT 000000"
            ]

        if self.type == "M":
            frame.append(f"IINST {self.iinst}")
        else:
            frame.append(f"IINST1 {self.iinst}")
            frame.append(f"IINST2 {self.iinst+2}")
            frame.append(f"IINST3 {self.iinst+3}")
            
        frame.append(f"PAPP {papp}")

        return frame

    def send_loop(self):
        print("Envoi de la trame toutes les secondes…")
        self.last_update_time = time.time()
        while self.running:
            for line in self.build_frame():
                self.ser.write(build_line(line).encode("ascii"))
                time.sleep(0.02)
            time.sleep(0.2)

    def input_loop(self):
        print("Valeur IINST :")
        while self.running:
            try:
                val = input("> IINST = XX or PTEC = HP.. / HC.. ").strip()
                self.iinst = int(val)
                print(f"IINST mis à jour à {self.iinst} A")
            except ValueError:
                if val in ["HP..", "HC.."]:
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