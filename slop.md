---
trigger: manual
---

================================================================================
AI SYSTEM DIRECTIVE: ANTI-SLOP DESIGN & ORGANIC MOTION ENGINE

Versi       : 2.4.0 (Production Grade)
Kategori    : UI/UX Engineering, Editorial Layout, Kinematics & Motion Design
Tujuan      : Mengeliminasi pola generik AI ("AI Slop"), menghasilkan desain modern,
editorial, taktil, dan memiliki animasi alami berbasis fisika nyata.

[1. FILOSOFI UTAMA: APA ITU "AI SLOP" VS "ELITE DESIGN"]

AI Slop dalam desain dicirikan oleh:

Penggunaan warna gradien ungu-biru neon (generic cyber glow).

Efek glassmorphism berlebihan (blur tinggi tanpa hierarki struktural).

Elemen mengambang 3D/geometri abstrak tanpa korelasi konteks fungsional.

Animasi kaku, linear, serentak, atau looping bounce tanpa inersia.

Layout kartu tiga kolom simetris yang membosankan dan teks generik.

Prinsip Elite Anti-Slop:

Intentional Hierarchy : Setiap piksel dan spasi memiliki alasan fungsional.

Tonal Restraint      : Warna monokromatis terkalibrasi dengan aksen tunggal berani.

Kinematic Physics    : Gerakan mengikuti hukum inersia, tegangan pegas, dan massa.

Editorial Precision  : Tipografi berbobot, kontras skala tegas, grid asimetris.

[2. VISUAL ARCHITECTURE (ANTI-SLOP GUIDELINES)]

A. SISTEM WARNA (NEUTRAL CORE + ACCENT VOLTAGE)

Dilarang: Palet default Tailwind ungu-violet, cyan glowing, dan gradien pelangi.

Gunakan:

Dark Mode : Deep Obsidian (#0B0C0E), Graphite (#16181D), Warm Zinc (#1C1E24).

Light Mode: Alabaster (#F8F8F6), Bone (#EFEFE9), Cool Titanium (#E4E6EB).

Border    : 1px hairline solid dengan opasitas rendah (rgba(255,255,255,0.08)
atau rgba(0,0,0,0.06)).

Accent    : Tepat SATU warna aksen bertaraf tinggi:
- Acid Lime   : #D4FF00
- Safety Alert: #FF4400
- Electric Blue: #0047FF
- Terminal Emerald: #00E599

B. TIPOGRAFI & SISTEM GRID

Padukan jenis Typeface dengan kontras tegangan tinggi:

Headline: Editorial Display Serif tajam ATAU Heavy Neo-Grotesque (tight tracking).

Data/Label: Monospaced teknis (e.g., JetBrains Mono, Geist Mono).

Body: Clean Humanist/Neutral Sans (Geist, Inter Display dengan tracking terkontrol).

Terapkan rhythm spasi tegas: kelipatan 4px / 8px dengan margin asimetris.

Gunakan rasio whitespace yang berani, jangan mengisi setiap ruang kosong.

C. KEDALAMAN (SURFACE & DEPTH)

Hindari: box-shadow: 0 20px 50px rgba(0,0,0,0.5) yang kabur dan kotor.

Gunakan: Multi-layered sharp shadows (rim shadows) dipadukan dengan hairline borders:
box-shadow:
0 1px 1px rgba(0, 0, 0, 0.05),
0 2px 4px rgba(0, 0, 0, 0.05),
0 8px 24px rgba(0, 0, 0, 0.08);

[3. ANIMATION & MOTION KINEMATICS (ORGANIC & NON-STIFF)]

Masalah utama animasi buatan AI adalah:

Terlalu seragam (semua elemen muncul bersamaan).

Memakai kurva matematis linear atau ease-in-out bawaan browser.

Jarak pergeseran terlalu jauh sehingga terlihat murah.

Standar Koreografi & Fisika Gerak:

A. TIMING & ACCELERATION CURVES

Entri Cepat & Henti Halus (Quintic Ease Out):
cubic-bezier(0.16, 1, 0.3, 1)
Durasi: 240ms - 360ms. Memberikan responsivitas instan tanpa jeda tumpul.

Interaksi Mikro / Snap Tactile (Hover & Click):
cubic-bezier(0.34, 1.56, 0.64, 1) -> Spring overshoot yang sangat mikro (< 2%).
Durasi: 120ms - 180ms.

Transisi Layar / Exit:
cubic-bezier(0.7, 0, 0.84, 0)
Durasi: 150ms - 200ms (Keluar selalu lebih cepat dibanding masuk).

B. CHOREOGRAPHY & STAGGER

Dilarang menganimasikan kontainer dan anak elemen secara serempak.

Terapkan stagger index offset:

Jeda antar elemen (delay): $25\text{ms}$ hingga $45\text{ms}$.

Urutan arah: Mengikuti hierarki bacaan mata (kiri-atas ke kanan-bawah).

C. SPATIAL DISPLACEMENT & MASS

Translasi perpindahan (Y-axis): Jangan pernah melempar elemen dari $50\text{px}$ ke bawah.
Gunakan micro-shift presisi: Translasi $8\text{px}$ hingga $14\text{px}$ saja.

Skala mikro: Mulai dari scale(0.97) ke scale(1.00).

Inersia: Elemen berat (dialog modal/card) bergerak lebih lambat dengan damping tinggi;
elemen ringan (tooltip, badge) bergerak lebih reaktif.

[4. SPESIFIKASI KODE FRAMEWORK]

A. FRAMER MOTION (REACT) - STANDAR ORGANIK

// Konfigurasi Spring Organik (Bukan Linear)
export const transitionSpring = {
  type: "spring",
  stiffness: 380,
  damping: 30,
  mass: 0.8,
};

// Container Stagger
export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.04,
      delayChildren: 0.08,
    },
  },
};

// Child Item Transition (Micro-displacement)
export const itemVariants = {
  hidden: { 
    opacity: 0, 
    y: 10, 
    filter: "blur(4px)",
    scale: 0.98 
  },
  visible: { 
    opacity: 1, 
    y: 0, 
    filter: "blur(0px)",
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 28,
    }
  },
};


B. CSS TOKEN & TAILWIND EXTENSION

:root {
  --ease-out-quint: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-expo: cubic-bezier(0.7, 0, 0.84, 0);
  --ease-spring-subtle: cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* Animasi entri berbobot */
.animate-enter-tactile {
  animation: enterTactile 280ms var(--ease-out-quint) forwards;
}

@keyframes enterTactile {
  0% {
    opacity: 0;
    transform: translateY(8px) scale(0.985);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}


[5. THE BLACKLIST: DAFTAR POLA TERLARANG]

[X] DILARANG: Card background transparan dengan blur 40px bertumpuk tanpa kontras jelas.
[X] DILARANG: Teks "AI-Powered Next-Gen Solution" atau copywriting klise sejenisnya.
[X] DILARANG: Tombol dengan gradien cyan ke ungu dengan efek sinar neon (neon glow bloom).
[X] DILARANG: Animasi elemen melayang terus-menerus (infinite hovering badge) tanpa interaksi.
[X] DILARANG: Tooltip atau dropdown yang muncul dengan efek perbesaran raksasa (scale 0 to 1).
[X] DILARANG: Ikon ilustratif 3D mengkilap yang tidak memiliki makna navigasi atau status.

[6. ATURAN PROMPTING KE MODEL AI]

Ketika Anda memberikan instruksi pembuatan UI/Komponen ke LLM/Figma AI/Cursor,
selipkan blok parameter wajib ini:

"Instruksi Gaya: Terapkan prinsip Anti-Slop Industrial & Editorial. Gunakan palet
monokromatis netral dengan hairline 1px borders (8% opacity), tipografi monospaced
untuk data teknis, dan satu warna aksen berbobot tinggi. Hindari gradien ungu
dan glassmorphism berlebih. Untuk motion/animasi, gunakan Framer Motion dengan
spring physics (stiffness: 380, damping: 30) atau CSS cubic-bezier(0.16, 1, 0.3, 1).
Gunakan micro-displacement maksimal 8-12px, blur entry 4px ke 0px, dan staggered delay
30ms antar item."