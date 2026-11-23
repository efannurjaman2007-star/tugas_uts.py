from datetime import datetime


class Produk:
    def __init__(self, kode, nama, harga, stok):
        self.kode = kode.upper()
        self.nama = nama
        self.harga = harga
        self.stok = stok

    @property
    def harga(self):
        return self.__harga

    @harga.setter
    def harga(self, nilai):
        if nilai < 0:
            raise ValueError("Harga tidak boleh negatif")
        self.__harga = float(nilai)

    @property
    def stok(self):
        return self.__stok

    @stok.setter
    def stok(self, nilai):
        if not isinstance(nilai, int) or nilai < 0:
            raise ValueError("Stok tidak valid")
        self.__stok = nilai

    @classmethod
    def dari_teks(cls, teks):
        kode, nama, harga, stok = teks.split("|")
        return cls(kode, nama, float(harga), int(stok))

class Transaksi:
    def __init__(self, nomor, barang, subtotal, diskon, bayar):
        self.nomor = nomor
        self.tanggal = datetime.now()
        self.barang = barang
        self.subtotal = subtotal
        self.diskon = diskon
        self.total = subtotal - diskon
        self.bayar = bayar
        self.kembalian = bayar - self.total

class Kasir:
    BATAS_DISKON = 100000
    PERSEN_DISKON = 10

    def __init__(self, nama_toko):
        self.nama_toko = nama_toko
        self.__produk = {}
        self.__keranjang = {}
        self.__riwayat = []

    @staticmethod
    def rupiah(angka):
        return "Rp" + f"{angka:,.0f}".replace(",", ".")

    @classmethod
    def hitung_diskon(cls, total):
        if total >= cls.BATAS_DISKON:
            return total * cls.PERSEN_DISKON / 100
        return 0

    def tambah_produk(self, produk):
        if produk.kode in self.__produk:
            print("Kode produk sudah digunakan!")
        else:
            self.__produk[produk.kode] = produk
            print("Produk berhasil ditambahkan!")

    def tampilkan_produk(self):
        print("\n========== DAFTAR PRODUK ==========")
        print(f"{'KODE':<8}{'NAMA':<20}{'HARGA':>14}{'STOK':>7}")
        for p in self.__produk.values():
            print(f"{p.kode:<8}{p.nama:<20}"
                  f"{self.rupiah(p.harga):>14}{p.stok:>7}")
        print("===================================")

    def ubah_produk(self, kode, harga=None, stok=None):
        p = self.__produk.get(kode.upper())

        if not p:
            print("Produk tidak ditemukan!")
            return

        try:
            if harga is not None:
                p.harga = harga
            if stok is not None:
                p.stok = stok
            print("Produk berhasil diubah!")
        except ValueError as e:
            print(e)

    def tambah_keranjang(self, kode, jumlah):
        p = self.__produk.get(kode.upper())

        if not p:
            print("Produk tidak ditemukan!")
        elif jumlah <= 0:
            print("Jumlah harus lebih dari 0!")
        elif self.__keranjang.get(kode.upper(), 0) + jumlah > p.stok:
            print("Stok tidak mencukupi!")
        else:
            kode = kode.upper()
            self.__keranjang[kode] = (
                self.__keranjang.get(kode, 0) + jumlah
            )
            print("Produk berhasil dimasukkan ke keranjang!")

    def hapus_keranjang(self, kode, jumlah=None):
        kode = kode.upper()

        if kode not in self.__keranjang:
            print("Produk tidak ada di keranjang!")
        elif jumlah is None or jumlah >= self.__keranjang[kode]:
            del self.__keranjang[kode]
            print("Produk berhasil dihapus!")
        elif jumlah > 0:
            self.__keranjang[kode] -= jumlah
            print("Jumlah produk berhasil dikurangi!")
        else:
            print("Jumlah tidak valid!")

    def tampilkan_keranjang(self):
        if not self.__keranjang:
            print("Keranjang masih kosong!")
            return

        subtotal = 0
        print("\n========== KERANJANG ==========")

        for kode, jumlah in self.__keranjang.items():
            p = self.__produk[kode]
            total = p.harga * jumlah
            subtotal += total
            print(f"{p.nama} x{jumlah} = {self.rupiah(total)}")

        diskon = self.hitung_diskon(subtotal)
        print("-------------------------------")
        print("Subtotal :", self.rupiah(subtotal))
        print("Diskon   :", self.rupiah(diskon))
        print("Total    :", self.rupiah(subtotal - diskon))

    def checkout(self):
        if not self.__keranjang:
            print("Keranjang masih kosong!")
            return

        subtotal = sum(
            self.__produk[k].harga * j
            for k, j in self.__keranjang.items()
        )

        diskon = self.hitung_diskon(subtotal)
        total = subtotal - diskon

        print("\n========== PEMBAYARAN ==========")
        print("Subtotal :", self.rupiah(subtotal))
        print("Diskon   :", self.rupiah(diskon))
        print("Total    :", self.rupiah(total))

        try:
            bayar = float(input("Uang pembayaran: Rp"))
        except ValueError:
            print("Pembayaran tidak valid!")
            return

        if bayar < total:
            print("Uang pembayaran kurang!")
            return

        barang = []
        for kode, jumlah in self.__keranjang.items():
            p = self.__produk[kode]
            barang.append((p.nama, jumlah, p.harga))
        
        for kode, jumlah in self.__keranjang.items():
            self.__produk[kode].stok -= jumlah

        transaksi = Transaksi(
            f"TRX{len(self.__riwayat) + 1:03d}",
            barang, subtotal, diskon, bayar
        )

        self.__riwayat.append(transaksi)
        self.__keranjang.clear()
        self.cetak_struk(transaksi)

    def cetak_struk(self, t):
        print("\n" + "=" * 42)
        print(self.nama_toko.center(42))
        print("STRUK PEMBAYARAN".center(42))
        print("=" * 42)
        print("Nomor   :", t.nomor)
        print("Tanggal :", t.tanggal.strftime("%d-%m-%Y %H:%M"))
        print("-" * 42)

        for nama, jumlah, harga in t.barang:
            print(f"{nama} x{jumlah}")
            print("Harga :", self.rupiah(harga * jumlah))

        print("-" * 42)
        print("Subtotal  :", self.rupiah(t.subtotal))
        print("Diskon    :", self.rupiah(t.diskon))
        print("Total     :", self.rupiah(t.total))
        print("Bayar     :", self.rupiah(t.bayar))
        print("Kembalian :", self.rupiah(t.kembalian))
        print("=" * 42)
        print("Terima kasih telah berbelanja!")

    def riwayat_transaksi(self):
        print("\n========== RIWAYAT TRANSAKSI ==========")

        if not self.__riwayat:
            print("Belum ada transaksi!")
            return

        for t in self.__riwayat:
            print(
                t.nomor,
                t.tanggal.strftime("%d-%m-%Y %H:%M"),
                self.rupiah(t.total)
            )

        nomor = input("Nomor transaksi untuk melihat struk (Enter untuk kembali): ").upper()

        for t in self.__riwayat:
            if t.nomor == nomor and nomor:
                self.cetak_struk(t)
                return

        if nomor:
            print("Transaksi tidak ditemukan!")

    def laporan_penjualan(self):
        if not self.__riwayat:
            print("Belum ada penjualan!")
            return

        produk_terjual = {}

        for t in self.__riwayat:
            for nama, jumlah, harga in t.barang:
                produk_terjual[nama] = (
                    produk_terjual.get(nama, 0) + jumlah
                )

        print("\n========== LAPORAN PENJUALAN ==========")
        print("Jumlah transaksi :", len(self.__riwayat))
        print("Barang terjual   :", sum(produk_terjual.values()))
        print("Total pendapatan :", self.rupiah(
            sum(t.total for t in self.__riwayat)
        ))
        print("Total diskon     :", self.rupiah(
            sum(t.diskon for t in self.__riwayat)
        ))

        for nama, jumlah in produk_terjual.items():
            print(nama, ":", jumlah, "unit")

        terlaris = max(produk_terjual, key=produk_terjual.get)
        print("Produk terlaris  :", terlaris)

def input_angka(pesan, tipe=int):
    while True:
        try:
            nilai = tipe(input(pesan))
            if nilai < 0:
                print("Angka tidak boleh negatif!")
            else:
                return nilai
        except ValueError:
            print("Masukkan angka yang benar!")


def main():
    kasir = Kasir("TOKO MAJU JAYA")

    kasir.tambah_produk(Produk("P001", "Buku Tulis", 5000, 30))
    kasir.tambah_produk(Produk("P002", "Pulpen", 3000, 50))
    kasir.tambah_produk(Produk("P003", "Penggaris", 4000, 20))
    kasir.tambah_produk(Produk("P004", "Tas Sekolah", 85000, 10))

    while True:
        print("\n====================================")
        print("       SISTEM KASIR SEDERHANA")
        print("           TOKO MAJU JAYA")
        print("====================================")
        print("1. Lihat daftar produk")
        print("2. Tambah produk")
        print("3. Ubah harga atau stok")
        print("4. Tambah ke keranjang")
        print("5. Lihat keranjang")
        print("6. Hapus barang dari keranjang")
        print("7. Checkout / pembayaran")
        print("8. Riwayat transaksi")
        print("9. Laporan penjualan")
        print("10. Keluar")
        print("====================================")

        pilih = input("Pilih menu (1-10): ")

        if pilih == "1":
            kasir.tampilkan_produk()

        elif pilih == "2":
            kode = input("Kode produk: ")
            nama = input("Nama produk: ")
            harga = input_angka("Harga: Rp", float)
            stok = input_angka("Stok: ")
            kasir.tambah_produk(Produk(kode, nama, harga, stok))

        elif pilih == "3":
            kasir.tampilkan_produk()
            kode = input("Kode produk: ")
            h = input("Harga baru (Enter jika tetap): ")
            s = input("Stok baru (Enter jika tetap): ")
            try:
                kasir.ubah_produk(
                    kode,
                    float(h) if h else None,
                    int(s) if s else None
                )
            except ValueError:
                print("Data harga atau stok tidak valid!")

        elif pilih == "4":
            kasir.tampilkan_produk()
            kode = input("Kode produk: ")
            jumlah = input_angka("Jumlah: ")
            kasir.tambah_keranjang(kode, jumlah)

        elif pilih == "5":
            kasir.tampilkan_keranjang()

        elif pilih == "6":
            kasir.tampilkan_keranjang()
            kode = input("Kode produk: ")
            jumlah = input("Jumlah yang dihapus (Enter untuk semua): ")
            try:
                kasir.hapus_keranjang(
                    kode, int(jumlah) if jumlah else None
                )
            except ValueError:
                print("Jumlah tidak valid!")

        elif pilih == "7":
            kasir.checkout()

        elif pilih == "8":
            kasir.riwayat_transaksi()

        elif pilih == "9":
            kasir.laporan_penjualan()

        elif pilih == "10":
            print("Terima kasih. Program selesai!")
            break

        else:
            print("Pilihan tidak tersedia!")


if __name__ == "__main__":
    main() 