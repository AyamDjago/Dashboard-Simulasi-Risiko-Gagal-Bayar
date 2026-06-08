import mesa
import random

# 1. KELAS AGEN (NASABAH)
class NasabahAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        # Nilai sekarang mengambil dari pengaturan slider di model
        self.FI = random.uniform(1.0, self.model.maks_boros) 
        self.FB = random.uniform(0.0, self.model.maks_tabungan)  
        self.DR = random.uniform(0.0, 0.1)  
        self.status = "Lancar"              

    def step(self):
        if self.status == "Gagal Bayar":
            return

        # Guncangan ekonomi sesuai slider Streamlit
        ES = random.uniform(0.0, self.model.maks_guncangan)
        LI = 0.0 

        if self.model.gunakan_intervensi and self.status == "Restrukturisasi":
            LI = self.model.kekuatan_intervensi # Keringanan sesuai slider

        beban_guncangan = max(0, (ES * self.FI) - self.FB)
        self.DR = self.DR + beban_guncangan - LI
        self.DR = max(0.0, self.DR) # Tidak boleh minus

        if self.DR >= 1.0:
            self.status = "Gagal Bayar"
        elif self.DR >= 0.8:
            self.status = "Restrukturisasi"
        elif self.DR >= 0.3:
            self.status = "Berisiko"
        else:
            self.status = "Lancar"

# 2. KELAS MODEL (LINGKUNGAN LEASING)
class LeasingModel(mesa.Model):
    # Tambahan parameter untuk menerima input dari Streamlit
    def __init__(self, N, gunakan_intervensi=False, maks_guncangan=0.5, maks_tabungan=0.5, maks_boros=2.0, kekuatan_intervensi=0.2, seed=None):
        super().__init__(seed=seed)
        self.num_agents = N
        self.gunakan_intervensi = gunakan_intervensi
        
        # Menyimpan parameter dari slider
        self.maks_guncangan = maks_guncangan
        self.maks_tabungan = maks_tabungan
        self.maks_boros = maks_boros
        self.kekuatan_intervensi = kekuatan_intervensi
        
        for _ in range(self.num_agents):
            NasabahAgent(self)

        self.datacollector = mesa.datacollection.DataCollector(
            model_reporters={"Rata_Rata_Risiko": self.compute_avg_dr}
        )

    def compute_avg_dr(self):
        agent_drs = [agent.DR for agent in self.agents]
        return sum(agent_drs) / len(agent_drs) if len(agent_drs) > 0 else 0

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")