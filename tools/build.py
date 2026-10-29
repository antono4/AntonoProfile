#!/usr/bin/env python3
"""Assemble the ANTONO static site from shared partials + page data.

Run:  python3 tools/build.py
Output: index.html, projects.html, blog.html, resume.html, contacts.html,
        404.html, robots.txt, sitemap.xml, manifest.webmanifest
"""
import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

SITE = {
    "name": "Antono",
    "tagline": "Ekosistem teknologi personal",
    "owner": "Antono",
    "email_work": "halo@antono.dev",
    "email_project": "studio@antono.dev",
    "location": "Jakarta, Indonesia",
    "role": "System Engineer / Full-Stack Developer",
    "url": "https://antono4.github.io/AntonoProfile",
    "github": "https://github.com/antono4",
    "og_image": "assets/img/og-cover.png",
    "locale": "id_ID",
}

# Derived so the wordmark can never drift from the brand name.
SITE["wordmark_head"] = SITE["name"][:1]
SITE["wordmark_tail"] = SITE["name"][1:]

# --------------------------------------------------------------------------
# Icons (lucide-style, 24x24 stroke geometry)
# --------------------------------------------------------------------------
ICONS = {
    "code": '<path d="m18 16 4-4-4-4"/><path d="m6 8-4 4 4 4"/><path d="m14.5 4-5 16"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20Z"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8M16 13H8M16 17H8"/>',
    "boxes": '<path d="M2.97 12.92A2 2 0 0 0 2 14.63v3.24a2 2 0 0 0 .97 1.71l3 1.8a2 2 0 0 0 2.06 0L12 19v-5.5l-5.5-3-3.53 1.42Z"/><path d="m7 16.5-4.74-2.85M12 13.5l-4.74 2.85M12 13.5V19"/><path d="M14 3.5 8.5 6.5 14 9.5l5.5-3L14 3.5Z"/><path d="m14 9.5 5.5-3v6l-5.5 3-5.5-3"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "github": '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
    "gitlab": '<path d="m22 13.29-3.33-10a.42.42 0 0 0-.14-.18.38.38 0 0 0-.22-.11.39.39 0 0 0-.23.07.42.42 0 0 0-.14.18l-2.26 6.67H8.32L6.1 3.26a.42.42 0 0 0-.14-.18.38.38 0 0 0-.23-.07.39.39 0 0 0-.22.11.42.42 0 0 0-.14.18l-3.33 10a.47.47 0 0 0 .18.55l10.2 7.4a.47.47 0 0 0 .56 0l10.2-7.4a.47.47 0 0 0 .18-.55Z"/>',
    "send": '<path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11l3.18 7.93Z"/><path d="m21.854 2.147-10.94 10.939"/>',
    "terminal": '<path d="m4 17 6-6-6-6"/><path d="M12 19h8"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.5-9.17 4.16a2 2 0 0 1-1.66 0L2 12.5"/><path d="m22 17.5-9.17 4.16a2 2 0 0 1-1.66 0L2 17.5"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76Z"/>',
    "sparkles": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0Z"/><path d="M20 3v4M22 5h-4M4 17v2M5 18H3"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "arrow-down": '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    "calendar": '<path d="M8 2v4M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1Z"/>',
    "server": '<rect width="20" height="8" x="2" y="2" rx="2"/><rect width="20" height="8" x="2" y="14" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
    "video": '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09Z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2Z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "briefcase": '<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "graduation": '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0Z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
    "award": '<path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/>',
    "map": '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0Z"/><path d="M15 5.764v15M9 3.236v15"/>',
    "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92Z"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6Z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
}


def icon(name, cls="", size=None):
    body = ICONS.get(name, ICONS["sparkles"])
    attrs = ' class="%s"' % cls if cls else ""
    dims = ' width="%s" height="%s"' % (size, size) if size else ""
    return (
        '<svg%s viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"%s>%s</svg>'
        % (attrs, dims, body)
    )


def esc(value):
    return html.escape(str(value), quote=True)


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
NAV = [
    ("index.html", "Beranda", "home"),
    ("projects.html", "Proyek", "boxes"),
    ("blog.html", "Blog", "book"),
    ("resume.html", "Resume", "file"),
    ("contacts.html", "Kontak", "mail"),
]

STATS = [
    ("data-count-to", 24, "Proyek"),
    ("data-count-to", 6, "Ekosistem"),
    ("data-count-to", 9, "Portal Pengetahuan"),
    ("data-count-to", 15, "Alat"),
    ("data-count-to", 12, "Kategori"),
    ("data-count-to", 148, "Publikasi"),
    ("data-count-to", 7, "Sumber Impor"),
    ("data-count-to", 4, "Kanal Video"),
]

ECOSYSTEMS = [
    {
        "key": "unifier",
        "name": "Unifier",
        "icon": "cpu",
        "desc": "Sistem terdistribusi untuk mengelola agen yang terhubung secara sukarela dan menggabungkannya menjadi klaster logis. Tujuannya membangun ruang digital tunggal untuk kontrol, otomasi, dan interaksi perangkat.",
        "projects": 5,
        "categories": 2,
        "tags": ["distributed", "automation", "iot"],
    },
    {
        "key": "antono-core",
        "name": "Antono Core",
        "icon": "layers",
        "desc": "Hub merek personal, produk, eksperimen, dan infrastruktur. Menyatukan reverse engineering dan arah rekayasa dalam satu tempat.",
        "projects": 8,
        "categories": 4,
        "tags": ["infrastructure", "reverse-engineering"],
    },
    {
        "key": "templates",
        "name": "Antono Templates",
        "icon": "boxes",
        "desc": "Template proyek dan starter kit untuk mempercepat pengembangan: boilerplate frontend, kerangka layanan, dan konfigurasi CI.",
        "projects": 6,
        "categories": 3,
        "tags": ["starter", "boilerplate", "ci"],
    },
    {
        "key": "tools",
        "name": "Antono Tools",
        "icon": "wrench",
        "desc": "Alat, utilitas, dan repositori rekayasa yang dipakai sehari-hari: CLI internal, generator, dan perkakas pengujian.",
        "projects": 5,
        "categories": 2,
        "tags": ["cli", "utility", "developer-tools"],
    },
    {
        "key": "docs",
        "name": "Antono Docs",
        "icon": "book",
        "desc": "Koleksi portal pengetahuan, dokumentasi, dan buku referensi yang disusun ulang agar mudah dicari dan dikutip.",
        "projects": 4,
        "categories": 3,
        "tags": ["docs", "knowledge", "reference"],
    },
    {
        "key": "atlas",
        "name": "Atlas",
        "icon": "map",
        "desc": "Platform produk dan pendidikan dengan layanan pembelajaran, modul terstruktur, serta pelacakan kemajuan.",
        "projects": 3,
        "categories": 2,
        "tags": ["product", "education"],
    },
]

CATEGORIES = [
    ("lizerium-servers", "Server Lizerium", "Server yang dijalankan untuk infrastruktur Lizerium", 4),
    ("lizerium-frameworks", "Framework Lizerium", "Framework yang dibangun dalam pengembangan ekosistem", 3),
    ("project-templates", "Template Proyek", "Proyek template untuk perancangan cepat", 6),
    ("test-tasks", "Tugas Uji", "Tugas uji yang diselesaikan sepanjang perjalanan", 9),
    ("servers", "Server", "Server yang dibuat saat ekosistem berkembang", 7),
    ("knowledge-portals", "Situs & Portal", "Portal pengetahuan yang dibangun di jaringan", 5),
]

PROJECTS = [
    {
        "slug": "unifier",
        "name": "Unifier",
        "eco": "Unifier",
        "icon": "cpu",
        "desc": "Platform orkestrasi agen terdistribusi dengan penemuan otomatis, klaster logis, dan kanal telemetri real-time.",
        "stack": ["C#", ".NET 8", "gRPC", "PostgreSQL"],
        "status": "Aktif",
        "stars": 412,
        "updated": "2026-06-02",
        "tags": ["distributed", "automation", "iot", "featured"],
    },
    {
        "slug": "atlas-learning",
        "name": "Atlas Learning",
        "eco": "Atlas",
        "icon": "graduation",
        "desc": "Layanan pembelajaran modular dengan jalur terstruktur, kuis adaptif, dan dasbor kemajuan.",
        "stack": ["TypeScript", "Next.js", "Prisma"],
        "status": "Aktif",
        "stars": 186,
        "updated": "2026-05-21",
        "tags": ["product", "education", "featured"],
    },
    {
        "slug": "localization-toolkit",
        "name": "Localization Toolkit",
        "eco": "Antono Tools",
        "icon": "wrench",
        "desc": "Perangkat lokalisasi .resx: editor GUI, contoh aplikasi, dan ekstensi Visual Studio untuk alur kerja terjemahan.",
        "stack": ["C#", "WPF", "VSIX"],
        "status": "Rilis v1.0.5",
        "stars": 97,
        "updated": "2026-05-07",
        "tags": ["cli", "utility", "developer-tools", "featured"],
    },
    {
        "slug": "knowledge-atlas",
        "name": "Knowledge Atlas",
        "eco": "Antono Docs",
        "icon": "book",
        "desc": "Portal pencarian untuk catatan, dokumen, dan referensi dengan pengindeksan penuh dan kutipan tautan permanen.",
        "stack": ["Go", "SQLite FTS5", "HTMX"],
        "status": "Aktif",
        "stars": 154,
        "updated": "2026-04-28",
        "tags": ["docs", "knowledge", "reference"],
    },
    {
        "slug": "starter-forge",
        "name": "Starter Forge",
        "eco": "Antono Templates",
        "icon": "rocket",
        "desc": "Generator proyek dengan template frontend, layanan backend, dan pipeline CI siap pakai dalam satu perintah.",
        "stack": ["Node.js", "Plop", "GitHub Actions"],
        "status": "Aktif",
        "stars": 233,
        "updated": "2026-04-15",
        "tags": ["starter", "boilerplate", "ci"],
    },
    {
        "slug": "telemetry-bridge",
        "name": "Telemetry Bridge",
        "eco": "Unifier",
        "icon": "server",
        "desc": "Jembatan telemetri berlatensi rendah yang menormalkan sinyal perangkat menjadi aliran kejadian tunggal.",
        "stack": ["Rust", "MQTT", "ClickHouse"],
        "status": "Beta",
        "stars": 68,
        "updated": "2026-03-30",
        "tags": ["distributed", "iot", "observability"],
    },
    {
        "slug": "vault-audit",
        "name": "Vault Audit",
        "eco": "Antono Tools",
        "icon": "shield",
        "desc": "Pemindai konfigurasi untuk menemukan rahasia yang bocor dan kebijakan akses yang longgar pada repositori.",
        "stack": ["Go", "Rego", "Docker"],
        "status": "Aktif",
        "stars": 121,
        "updated": "2026-03-11",
        "tags": ["security", "cli", "developer-tools"],
    },
    {
        "slug": "atlas-bridge",
        "name": "Atlas Bridge",
        "eco": "Atlas",
        "icon": "layers",
        "desc": "Lapisan integrasi yang menyambungkan konten pembelajaran dengan sistem eksternal dan penyimpanan siswa.",
        "stack": ["TypeScript", "tRPC", "Redis"],
        "status": "Aktif",
        "stars": 54,
        "updated": "2026-02-24",
        "tags": ["product", "education", "infrastructure"],
    },
]

UPDATES = [
    {
        "date": "05.06.2026",
        "kind": "Artikel",
        "source": "Portal",
        "title": "Production AI Systems 2026: membangun platform RAG + AI Agents yang benar-benar berjalan",
        "text": "Panduan rekayasa praktis untuk RAG produksi, AI agents, tool calling, structured output, MCP, keamanan, observability, dan evaluasi.",
        "eco": "Antono Core",
        "tags": ["article", "ai", "featured"],
    },
    {
        "date": "02.06.2026",
        "kind": "Perubahan",
        "source": "Portal",
        "title": "Katalog awal diperluas",
        "text": "Data awal diisi dengan situs nyata, portal pengetahuan, alat, repositori, dan organisasi.",
        "eco": "Antono Core",
        "tags": ["changelog", "featured"],
    },
    {
        "date": "02.06.2026",
        "kind": "Perubahan",
        "source": "Portal",
        "title": "Proyek awal ditambahkan",
        "text": "Katalog mendapat kerangka pertama untuk pengisian berikutnya.",
        "eco": "Antono Core",
        "tags": ["changelog"],
    },
    {
        "date": "02.06.2026",
        "kind": "Berita",
        "source": "Portal",
        "title": "Peluncuran",
        "text": "Fondasi katalog proyek dan panel admin dibuat.",
        "eco": "Antono Core",
        "tags": ["news"],
    },
    {
        "date": "07.05.2026",
        "kind": "Video",
        "source": "YouTube",
        "title": "Visualisasi suara secara real-time - eksperimen Unifier",
        "text": "Menguji sistem visualisasi suara buatan sendiri untuk proyek Unifier: mengubah audio, ucapan, dan sinyal agen AI menjadi efek visual.",
        "eco": "Unifier",
        "tags": ["video", "ai"],
    },
    {
        "date": "07.05.2026",
        "kind": "Rilis",
        "source": "GitHub",
        "title": "v1.0.5 - Localization Toolkit",
        "text": "Rilis ini memperbarui paket NuGet dan menambahkan build baru untuk Visual Studio 2022.",
        "eco": "Antono Tools",
        "tags": ["release", "developer-tools"],
    },
    {
        "date": "06.05.2026",
        "kind": "Rilis",
        "source": "GitHub",
        "title": "v1.0.4 - Localization Toolkit",
        "text": "Menyertakan paket NuGet yang diperbarui dan VSIX baru untuk Visual Studio 2022.",
        "eco": "Antono Tools",
        "tags": ["release", "developer-tools"],
    },
    {
        "date": "05.05.2026",
        "kind": "Rilis",
        "source": "GitHub",
        "title": "v1.0.3 - Localization Toolkit",
        "text": "Rilis untuk lokalisasi .resx: editor GUI, contoh aplikasi, dan ekstensi VSIX.",
        "eco": "Antono Tools",
        "tags": ["release", "developer-tools"],
    },
    {
        "date": "04.05.2026",
        "kind": "Catatan",
        "source": "Blog",
        "title": "Mendesain pipeline telemetri yang tahan gangguan",
        "text": "Pelajaran dari menjalankan jembatan telemetri: backpressure, dead-letter queue, dan skema kejadian yang ketat.",
        "eco": "Unifier",
        "tags": ["article", "observability"],
    },
]

EXPERIENCE = [
    {
        "period": "2023 - Sekarang",
        "role": "Lead System Engineer",
        "org": "Antono Studio",
        "desc": "Memimpin arsitektur platform terdistribusi Unifier: perancangan protokol, model klaster, dan observability end-to-end. Menurunkan latensi p99 sebesar 43%.",
    },
    {
        "period": "2021 - 2023",
        "role": "Full-Stack Developer",
        "org": "Arunika Digital",
        "desc": "Membangun produk SaaS multi-tenant dari nol: API TypeScript, antarmuka React, dan pipeline rilis otomatis.",
    },
    {
        "period": "2019 - 2021",
        "role": "Backend Engineer",
        "org": "Pilar Data",
        "desc": "Merancang layanan data Go dengan throughput tinggi, migrasi basis data tanpa downtime, dan strategi caching berlapis.",
    },
    {
        "period": "2017 - 2019",
        "role": "Software Engineer",
        "org": "Studio Rekayasa Mandiri",
        "desc": "Menangani proyek klien lintas industri, dari desktop C# hingga alat otomasi internal.",
    },
]

SKILLS = [
    ("Backend & Distributed Systems", 0.94, "92%"),
    ("Infrastruktur & DevOps", 0.86, "86%"),
    ("Frontend Engineering", 0.82, "82%"),
    ("Observability & Reliability", 0.78, "78%"),
    ("Keamanan Aplikasi", 0.72, "72%"),
]

STACK = [
    ("Bahasa", ["C#", "TypeScript", "Go", "Rust", "Python", "SQL"]),
    ("Platform", [".NET 8", "Node.js", "Next.js", "React", "WPF", "VSIX"]),
    ("Data", ["PostgreSQL", "SQLite", "Redis", "ClickHouse", "Prisma"]),
    ("Infrastruktur", ["Docker", "GitHub Actions", "gRPC", "MQTT", "Linux", "Nginx"]),
]

EDUCATION = [
    ("2013 - 2017", "Sarjana Teknik Informatika", "Universitas Teknologi Nusantara", "Fokus sistem terdistribusi dan rekayasa perangkat lunak."),
    ("2024", "Sertifikasi Cloud Architecture", "Lembaga Sertifikasi Profesional", "Perancangan arsitektur cloud, keamanan, dan efisiensi biaya."),
]

CONTACTS = [
    ("mail", "Email Kerja", "halo@antono.dev", "mailto:halo@antono.dev"),
    ("mail", "Email Proyek", "studio@antono.dev", "mailto:studio@antono.dev"),
    ("github", "GitHub", "github.com/antono4", "https://github.com"),
    ("gitlab", "GitLab", "gitlab.com/antono4", "https://gitlab.com"),
    ("linkedin", "LinkedIn", "linkedin.com/in/antono", "https://www.linkedin.com"),
    ("map", "Lokasi", "Jakarta, Indonesia", "#"),
    ("phone", "Telepon", "+62 812 0000 0000", "tel:+6281200000000"),
    ("globe", "Situs", "antono.dev", "https://antono.dev"),
]

SOCIALS = [
    ("github", "GitHub", "https://github.com"),
    ("gitlab", "GitLab", "https://gitlab.com"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com"),
    ("mail", "Email", "mailto:halo@antono.dev"),
]


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def head(title, description, page_slug):
    # 404 must never be indexed; every other page advertises a canonical URL so
    # search engines do not treat the Pages host and any future domain as dupes.
    canonical = "%s/%s" % (SITE["url"], "" if page_slug == "index.html" else page_slug)
    robots = (
        "noindex, follow"
        if page_slug == "404.html"
        else "index, follow, max-image-preview:large"
    )
    og_image = "%s/%s" % (SITE["url"], SITE["og_image"])
    structured = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebSite",
                    "@id": "%s/#website" % SITE["url"],
                    "url": "%s/" % SITE["url"],
                    "name": SITE["name"],
                    "description": SITE["tagline"],
                    "inLanguage": "id-ID",
                    "publisher": {"@id": "%s/#person" % SITE["url"]},
                },
                {
                    "@type": "Person",
                    "@id": "%s/#person" % SITE["url"],
                    "name": SITE["owner"],
                    "url": "%s/" % SITE["url"],
                    "jobTitle": SITE["role"],
                    "image": "%s/%s" % (SITE["url"], "assets/img/avatar.jpg"),
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": SITE["location"],
                    },
                    "sameAs": [SITE["github"]],
                },
                {
                    "@type": "WebPage",
                    "@id": canonical,
                    "url": canonical,
                    "name": title,
                    "description": description,
                    "isPartOf": {"@id": "%s/#website" % SITE["url"]},
                    "inLanguage": "id-ID",
                },
            ],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")  # cannot close the surrounding <script> tag
    return """<!DOCTYPE html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="robots" content="%s">
<meta name="author" content="%s">
<meta name="theme-color" content="#0f131a">
<meta name="generator" content="Antono static builder">
<link rel="canonical" href="%s">
<link rel="icon" href="data:image/svg+xml,%s">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%s">
<meta property="og:locale" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="%s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/css/style.css">
<script type="application/ld+json">%s</script>
</head>
<body>
<a class="sr-only" href="#main">Lewati ke konten utama</a>
<div class="atmosphere" aria-hidden="true"></div>
<div class="grain" aria-hidden="true"></div>
<div class="page">
""" % (
        esc(title),
        esc(description),
        robots,
        esc(SITE["owner"]),
        esc(canonical),
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%230b1116'/%3E%3Cpath d='M10 22V10l12 12V10' stroke='%232dd4bf' stroke-width='3' fill='none' stroke-linecap='round'/%3E%3C/svg%3E",
        esc(SITE["name"]),
        esc(SITE["locale"]),
        esc(title),
        esc(description),
        esc(canonical),
        esc(og_image),
        esc("%s - %s" % (SITE["name"], SITE["tagline"])),
        esc(title),
        esc(description),
        esc(og_image),
        structured,
    )


def header(page_slug):
    links = []
    for href, label, ico in NAV:
        current = ' aria-current="page"' if href == page_slug else ""
        links.append(
            '<a class="nav__link" href="%s"%s>%s<span>%s</span></a>'
            % (href, current, icon(ico), esc(label))
        )
    return """<header class="site-header">
  <div class="shell site-header__inner">
    <a class="brand" href="index.html">
      <span class="brand__mark">%s</span>
      <span class="brand__name">%s</span>
    </a>
    <nav class="nav" id="primary-nav" data-open="false" aria-label="Navigasi utama">
      %s
    </nav>
    <div class="header-tools">
      <button class="icon-btn" type="button" data-search-open aria-label="Buka pencarian" title="Pencarian (Ctrl+K)">%s</button>
      <button class="icon-btn" type="button" data-theme-toggle aria-label="Aktifkan tema terang" title="Ganti tema">%s%s</button>
      <button class="icon-btn nav-toggle" type="button" data-nav-toggle aria-label="Buka menu" aria-expanded="false" aria-controls="primary-nav">%s</button>
    </div>
  </div>
</header>
""" % (
        icon("code"),
        esc(SITE["name"]),
        "\n      ".join(links),
        icon("search"),
        icon("sun", cls="theme-icon-light"),
        icon("moon", cls="theme-icon-dark"),
        icon("menu"),
    )


def search_dialog():
    index = []
    for p in PROJECTS:
        index.append({"title": p["name"], "kind": "Proyek", "href": "projects.html"})
    for u in UPDATES:
        index.append({"title": u["title"], "kind": u["kind"], "href": "blog.html"})
    for e in ECOSYSTEMS:
        index.append({"title": e["name"], "kind": "Ekosistem", "href": "index.html#ekosistem"})
    for c in CATEGORIES:
        index.append({"title": c[1], "kind": "Kategori", "href": "projects.html"})
    index.append({"title": "Resume & Pengalaman", "kind": "Halaman", "href": "resume.html"})
    index.append({"title": "Kontak", "kind": "Halaman", "href": "contacts.html"})
    import json
    return """<div class="dialog" data-search-dialog data-open="false" data-index="%s" role="dialog" aria-modal="true" aria-label="Pencarian situs">
  <div class="dialog__panel">
    <div class="dialog__input-row">
      %s
      <input type="search" data-search-input placeholder="Cari proyek, catatan, ekosistem..." aria-label="Kata kunci pencarian">
      <kbd class="tag">ESC</kbd>
    </div>
    <div class="dialog__results" data-search-results></div>
  </div>
</div>
""" % (esc(json.dumps(index, ensure_ascii=False)), icon("search"))


def footer():
    eco_links = "\n".join(
        '<li><a href="projects.html">%s</a></li>' % esc(e["name"]) for e in ECOSYSTEMS
    )
    page_links = "\n".join(
        '<li><a href="%s">%s</a></li>' % (href, esc(label)) for href, label, _ in NAV
    )
    social_links = "\n".join(
        '<a href="%s" aria-label="%s" rel="noopener noreferrer" target="_blank">%s</a>'
        % (url, esc(label), icon(ico))
        for ico, label, url in SOCIALS
    )
    return """<footer class="site-footer">
  <div class="shell">
    <div class="footer__grid">
      <div>
        <p class="footer__title">%s</p>
        <p class="muted mt-4">Ekosistem produk, alat, portal pengetahuan, dan sistem rekayasa.</p>
        <p class="muted mono mt-2">%s</p>
      </div>
      <div>
        <p class="footer__title">Ekosistem</p>
        <ul class="footer__list">
          %s
        </ul>
      </div>
      <div>
        <p class="footer__title">Halaman</p>
        <ul class="footer__list">
          %s
        </ul>
      </div>
      <div>
        <p class="footer__title">Kontak</p>
        <ul class="footer__list">
          <li><a href="mailto:%s">%s</a></li>
          <li><a href="mailto:%s">%s</a></li>
          <li><span class="muted">%s</span></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <p>&copy; 2026 %s. Dibangun sebagai situs statis.</p>
      <div class="socials">
        %s
      </div>
    </div>
  </div>
</footer>
</div>
<script src="assets/js/main.js" defer></script>
</body>
</html>
""" % (
        esc(SITE["name"]),
        esc(SITE["role"]),
        eco_links,
        page_links,
        esc(SITE["email_work"]),
        esc(SITE["email_work"]),
        esc(SITE["email_project"]),
        esc(SITE["email_project"]),
        esc(SITE["location"]),
        esc(SITE["name"]),
        social_links,
    )


def page_hero(title, lede, crumb):
    return """<section class="page-hero">
  <div class="hero__halo" aria-hidden="true"></div>
  <div class="hero__topline" aria-hidden="true"></div>
  <div class="shell page-hero__inner">
    <nav class="crumbs" aria-label="Remah">
      <a href="index.html">Beranda</a><span aria-hidden="true">/</span><span>%s</span>
    </nav>
    <h1>%s</h1>
    <p>%s</p>
  </div>
</section>
""" % (esc(crumb), esc(title), esc(lede))


# --------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------
def stat_cards():
    out = []
    for _, value, label in STATS:
        out.append(
            '<div class="stat" data-reveal><p class="stat__value"><span data-count-to="%d">0</span></p>'
            '<p class="stat__label">%s</p></div>' % (value, esc(label))
        )
    return '<div class="stats">%s</div>' % "".join(out)


def ecosystem_card(eco):
    return """<article class="card" data-reveal data-tags="%s">
  <div class="card__top">
    <span class="card__icon">%s</span>
    <span class="tag">Ekosistem</span>
  </div>
  <h3 class="card__title">%s</h3>
  <p class="card__text">%s</p>
  <div class="card__meta"><span><b>%d</b> proyek</span><span><b>%d</b> kategori</span></div>
  <a class="card__link" href="projects.html">Jelajahi ekosistem %s %s</a>
</article>""" % (
        esc(" ".join(eco["tags"])),
        icon(eco["icon"]),
        esc(eco["name"]),
        esc(eco["desc"]),
        eco["projects"],
        eco["categories"],
        esc(eco["name"]),
        icon("arrow-right"),
    )


def category_card(cat):
    key, title, desc, count = cat
    return """<a class="cat-card" href="projects.html" data-reveal>
  <span class="cat-card__key">%s</span>
  <span class="cat-card__title">%s</span>
  <span class="cat-card__count">%d proyek &middot; %s</span>
</a>""" % (esc(key), esc(title), count, esc(desc))


def feed_item(update):
    tags = "".join('<span class="tag">%s</span>' % esc(t) for t in update["tags"])
    return """<article class="feed-item" data-reveal data-tags="%s">
  <div>
    <p class="feed-item__date">%s</p>
    <p class="mt-2"><span class="tag tag--accent">%s</span></p>
  </div>
  <div class="feed-item__body">
    <h3 class="feed-item__title">%s</h3>
    <p class="feed-item__text">%s</p>
    <div class="feed-item__tags">
      %s
      <span class="tag">%s</span>
      <span class="tag">%s</span>
    </div>
  </div>
</article>""" % (
        esc(" ".join(update["tags"])),
        esc(update["date"]),
        esc(update["kind"]),
        esc(update["title"]),
        esc(update["text"]),
        tags,
        esc(update["source"]),
        esc(update["eco"]),
    )


def project_card(project):
    stack = "".join("<span>%s</span>" % esc(s) for s in project["stack"])
    return """<article class="card" data-reveal data-tags="%s">
  <div class="card__top">
    <span class="card__icon">%s</span>
    <span class="tag tag--accent">%s</span>
  </div>
  <h3 class="card__title">%s</h3>
  <p class="card__slug">%s</p>
  <p class="card__text">%s</p>
  <div class="card__meta">
    <span><b>&#9733;</b> %d</span>
    <span>Diperbarui %s</span>
  </div>
  <div class="feed-item__tags mt-4">%s</div>
  <a class="card__link" href="projects.html">Lihat detail %s</a>
</article>""" % (
        esc(" ".join(project["tags"])),
        icon(project["icon"]),
        esc(project["status"]),
        esc(project["name"]),
        esc(project["eco"]),
        esc(project["desc"]),
        project["stars"],
        esc(project["updated"]),
        stack,
        icon("arrow-right"),
    )


def hero_plaques():
    words = [SITE["role"].split(" / ")[0], SITE["role"].split(" / ")[1], "System Engineer",
             "Full-Stack Developer", "Infrastruktur & Otomasi", "Observability & Keamanan"]
    return "".join(
        '<span class="plaque" data-plaque="%d">%s</span>' % (i + 1, esc(w))
        for i, w in enumerate(words)
    )


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def build_index():
    eco_cards = "".join(ecosystem_card(e) for e in ECOSYSTEMS)
    cat_cards = "".join(category_card(c) for c in CATEGORIES)
    feed = "".join(feed_item(u) for u in UPDATES[:6])
    page = head(
        "Antono - Ekosistem teknologi personal",
        "Ekosistem produk, alat, portal pengetahuan, dan sistem rekayasa. Proyek open source, catatan teknis, dan pengalaman rekayasa.",
        "index.html",
    )
    page += header("index.html")
    page += """<main id="main">
<section class="hero">
  <div class="hero__halo" aria-hidden="true"></div>
  <div class="hero__topline" aria-hidden="true"></div>
  <div class="hero__plaques" aria-hidden="true">%s</div>
  <div class="shell hero__grid">
    <div class="hero__copy">
      <h1 class="wordmark"><span class="wordmark__letter" aria-hidden="true">%s</span><span class="sr-only">%s</span><span>%s</span></h1>
      <div class="hero__signal">
        <p class="hero__signal-title"><span class="signal-dot" aria-hidden="true"></span>Ekosistem teknologi personal</p>
      </div>
      <p class="hero__lede">Membangun dan merawat sistem terdistribusi, alat rekayasa, dan portal pengetahuan. Semua proyek, catatan, dan eksperimen terkumpul di satu tempat yang bisa ditelusuri.</p>
      <div class="hero__roles">
        <span class="role-chip">%sSystem Engineer</span>
        <span class="role-chip">%sFull-Stack Developer</span>
        <span class="role-chip">%sOpen Source</span>
      </div>
      <div class="hero__cta">
        <a class="btn btn--primary" href="resume.html">%sBuka resume</a>
        <a class="btn btn--ghost" href="projects.html">%sLihat proyek</a>
        <a class="btn btn--quiet" href="contacts.html">%sHubungi</a>
      </div>
      <a class="hero__cue" href="#ekosistem">Jelajahi arah <span aria-hidden="true">&darr;</span></a>
    </div>
    <aside class="hero__panel" data-reveal>
      <div class="portrait">
        <img class="portrait__photo" src="assets/img/avatar.jpg" width="460" height="460" alt="Foto profil %s" loading="lazy" decoding="async">
        <span class="portrait__scan" aria-hidden="true"></span>
      </div>
      <dl class="panel-rows">
        <div class="panel-row"><dt>Peran</dt><dd>System Engineer</dd></div>
        <div class="panel-row"><dt>Fokus</dt><dd>Sistem terdistribusi</dd></div>
        <div class="panel-row"><dt>Basis</dt><dd>%s</dd></div>
        <div class="panel-row"><dt>Status</dt><dd>Terbuka untuk kolaborasi</dd></div>
      </dl>
    </aside>
  </div>
</section>
<section class="section section--tight">
  <div class="shell">%s</div>
</section>
<section class="section" id="ekosistem">
  <div class="shell">
    <div class="section__head" data-reveal>
      <p class="eyebrow">Peta arah</p>
      <h2 class="section__title">Ekosistem</h2>
      <p class="section__lede">Ekosistem dan kategori membantu berpindah ke arah yang tepat dengan cepat.</p>
    </div>
    <div class="grid grid--3">%s</div>
  </div>
</section>
<section class="section" id="kategori">
  <div class="shell">
    <div class="section__head" data-reveal>
      <p class="eyebrow">Navigasi berdasarkan makna</p>
      <h2 class="section__title">Kategori ekosistem</h2>
      <p class="section__lede">Kategori menghubungkan proyek, materi, dan sumber eksternal menjadi struktur yang mudah dipahami.</p>
    </div>
    <div class="grid grid--3">%s</div>
  </div>
</section>
<section class="section" id="pembaruan">
  <div class="shell">
    <div class="section__head section__head--row" data-reveal>
      <div>
        <p class="eyebrow">Blog &amp; sinkronisasi</p>
        <h2 class="section__title">Pembaruan terbaru</h2>
        <p class="section__lede">Publikasi menggabungkan catatan manual, materi impor, video, dan pembaruan rilis.</p>
      </div>
      <a class="btn btn--ghost" href="blog.html">Buka blog %s</a>
    </div>
    <div class="feed">%s</div>
  </div>
</section>
</main>
""" % (
        hero_plaques(),
        esc(SITE["wordmark_head"]),
        esc(SITE["wordmark_head"]),
        esc(SITE["wordmark_tail"]),
        icon("cpu"),
        icon("code"),
        icon("sparkles"),
        icon("file"),
        icon("boxes"),
        icon("mail"),
        esc(SITE["name"]),
        esc(SITE["location"]),
        stat_cards(),
        eco_cards,
        cat_cards,
        icon("arrow-right"),
        feed,
    )
    page += search_dialog()
    page += footer()
    return page


def build_projects():
    cards = "".join(project_card(p) for p in PROJECTS)
    filters = ['<button class="chip" type="button" data-filter="all" aria-pressed="true">Semua</button>']
    for value, label in [("featured", "Unggulan"), ("distributed", "Terdistribusi"), ("developer-tools", "Alat Developer"),
                         ("docs", "Dokumentasi"), ("education", "Pendidikan"), ("security", "Keamanan")]:
        filters.append(
            '<button class="chip" type="button" data-filter="%s" aria-pressed="false">%s</button>'
            % (value, esc(label))
        )
    page = head(
        "Proyek - Antono",
        "Katalog proyek: platform terdistribusi, alat developer, portal pengetahuan, dan eksperimen rekayasa.",
        "projects.html",
    )
    page += header("projects.html")
    page += page_hero(
        "Katalog proyek",
        "Semua proyek terbuka di satu tempat: platform, alat, portal, dan eksperimen. Saring berdasarkan arah atau cari dengan kata kunci.",
        "Proyek",
    )
    page += """<main id="main">
<section class="section">
  <div class="shell" data-filter-root>
    <div class="toolbar">
      <label class="field">%s<input type="search" data-search placeholder="Cari proyek..." aria-label="Cari proyek"></label>
      %s
    </div>
    <p class="muted mono">Menampilkan <b data-result-count>%d</b> proyek</p>
    <div class="grid grid--3 mt-6">%s</div>
    <p class="empty mt-6" data-empty hidden>Tidak ada proyek yang cocok dengan saringan ini.</p>
  </div>
</section>
</main>
""" % (icon("search"), "".join(filters), len(PROJECTS), cards)
    page += search_dialog()
    page += footer()
    return page


def build_blog():
    feed = "".join(feed_item(u) for u in UPDATES)
    filters = ['<button class="chip" type="button" data-filter="all" aria-pressed="true">Semua</button>']
    for value, label in [("article", "Artikel"), ("release", "Rilis"), ("changelog", "Perubahan"),
                         ("video", "Video"), ("news", "Berita"), ("featured", "Unggulan")]:
        filters.append(
            '<button class="chip" type="button" data-filter="%s" aria-pressed="false">%s</button>'
            % (value, esc(label))
        )
    page = head(
        "Blog dan pembaruan - Antono",
        "Catatan teknis, pembaruan rilis, video, dan changelog dari seluruh ekosistem.",
        "blog.html",
    )
    page += header("blog.html")
    page += page_hero(
        "Blog dan pembaruan",
        "Catatan rekayasa, changelog, rilis, dan video. Satu aliran yang menggabungkan tulisan manual dengan materi yang diimpor.",
        "Blog",
    )
    page += """<main id="main">
<section class="section">
  <div class="shell" data-filter-root>
    <div class="toolbar">
      <label class="field">%s<input type="search" data-search placeholder="Cari catatan..." aria-label="Cari catatan"></label>
      %s
    </div>
    <p class="muted mono">Menampilkan <b data-result-count>%d</b> catatan</p>
    <div class="feed mt-6">%s</div>
    <p class="empty mt-6" data-empty hidden>Tidak ada catatan yang cocok dengan saringan ini.</p>
  </div>
</section>
</main>
""" % (icon("search"), "".join(filters), len(UPDATES), feed)
    page += search_dialog()
    page += footer()
    return page


def build_resume():
    exp = "".join(
        """<article class="timeline__item" data-reveal>
  <p class="timeline__period">%s</p>
  <h3 class="timeline__role">%s</h3>
  <p class="timeline__org">%s</p>
  <p class="timeline__desc">%s</p>
</article>""" % (esc(e["period"]), esc(e["role"]), esc(e["org"]), esc(e["desc"]))
        for e in EXPERIENCE
    )
    edu = "".join(
        """<article class="timeline__item" data-reveal>
  <p class="timeline__period">%s</p>
  <h3 class="timeline__role">%s</h3>
  <p class="timeline__org">%s</p>
  <p class="timeline__desc">%s</p>
</article>""" % (esc(p), esc(t), esc(o), esc(d))
        for p, t, o, d in EDUCATION
    )
    skills = "".join(
        """<div data-reveal>
  <div class="skill__head"><span>%s</span><span>%s</span></div>
  <div class="skill__bar"><span class="skill__fill" style="--level: %.2f"></span></div>
</div>""" % (esc(name), esc(pct), level)
        for name, level, pct in SKILLS
    )
    stacks = "".join(
        """<div class="stack-group" data-reveal>
  <h3>%s</h3>
  <ul>%s</ul>
</div>""" % (esc(title), "".join("<li>%s</li>" % esc(item) for item in items))
        for title, items in STACK
    )
    page = head(
        "Resume - Antono",
        "Pengalaman, keterampilan, teknologi, dan pendidikan. Resume ringkas seorang system engineer dan full-stack developer.",
        "resume.html",
    )
    page += header("resume.html")
    page += page_hero(
        "Resume",
        "Ringkasan pengalaman rekayasa: kepemimpinan teknis pada platform terdistribusi, pengembangan produk, dan infrastruktur.",
        "Resume",
    )
    page += """<main id="main">
<section class="section">
  <div class="shell">
    <div class="section__head section__head--row" data-reveal>
      <div>
        <p class="eyebrow">Profil</p>
        <h2 class="section__title">%s</h2>
        <p class="section__lede">System engineer yang berfokus pada sistem terdistribusi, keandalan, dan alur kerja pengembangan yang rapi. Nyaman bergerak dari arsitektur hingga antarmuka.</p>
      </div>
      <a class="btn btn--primary" href="mailto:%s">%sHubungi saya</a>
    </div>
    <div class="stats">
      <div class="stat"><p class="stat__value"><span data-count-to="9">0</span>+</p><p class="stat__label">Tahun pengalaman</p></div>
      <div class="stat"><p class="stat__value"><span data-count-to="24">0</span></p><p class="stat__label">Proyek aktif</p></div>
      <div class="stat"><p class="stat__value"><span data-count-to="6">0</span></p><p class="stat__label">Ekosistem</p></div>
      <div class="stat"><p class="stat__value"><span data-count-to="4">0</span></p><p class="stat__label">Kanal video</p></div>
    </div>
  </div>
</section>
<section class="section section--tight">
  <div class="shell grid grid--2">
    <div>
      <div class="section__head" data-reveal>
        <p class="eyebrow">Pengalaman</p>
        <h2 class="section__title">Jejak karier</h2>
      </div>
      <div class="timeline">%s</div>
    </div>
    <div>
      <div class="section__head" data-reveal>
        <p class="eyebrow">Pendidikan dan sertifikasi</p>
        <h2 class="section__title">Latar belakang</h2>
      </div>
      <div class="timeline">%s</div>
    </div>
  </div>
</section>
<section class="section section--tight">
  <div class="shell grid grid--2">
    <div>
      <div class="section__head" data-reveal>
        <p class="eyebrow">Keterampilan</p>
        <h2 class="section__title">Bidang keahlian</h2>
      </div>
      <div class="skill-list">%s</div>
    </div>
    <div>
      <div class="section__head" data-reveal>
        <p class="eyebrow">Teknologi</p>
        <h2 class="section__title">Tumpukan teknologi</h2>
      </div>
      <div class="stack-groups">%s</div>
    </div>
  </div>
</section>
</main>
""" % (
        esc(SITE["role"]),
        esc(SITE["email_work"]),
        icon("send"),
        exp,
        edu,
        skills,
        stacks,
    )
    page += search_dialog()
    page += footer()
    return page


def build_contacts():
    cards = "".join(
        """<a class="contact-card" href="%s" data-reveal>
  <span class="contact-card__icon">%s</span>
  <span>
    <span class="contact-card__label">%s</span>
    <span class="contact-card__value">%s</span>
  </span>
</a>""" % (esc(url), icon(ico), esc(label), esc(value))
        for ico, label, value, url in CONTACTS
    )
    page = head(
        "Kontak - Antono",
        "Hubungi melalui email, GitHub, GitLab, atau LinkedIn. Terbuka untuk kolaborasi proyek dan konsultasi rekayasa.",
        "contacts.html",
    )
    page += header("contacts.html")
    page += page_hero(
        "Kontak",
        "Pilih kanal yang paling nyaman. Untuk pertanyaan proyek, sertakan konteks singkat agar balasan bisa lebih tepat.",
        "Kontak",
    )
    page += """<main id="main">
<section class="section">
  <div class="shell">
    <div class="section__head" data-reveal>
      <p class="eyebrow">Kanal utama</p>
      <h2 class="section__title">Cara menghubungi</h2>
    </div>
    <div class="contact-grid">%s</div>
  </div>
</section>
<section class="section section--tight">
  <div class="shell grid grid--2">
    <div>
      <div class="section__head" data-reveal>
        <p class="eyebrow">Pesan</p>
        <h2 class="section__title">Kirim pesan</h2>
        <p class="section__lede">Formulir ini berjalan di sisi klien. Hubungkan ke backend atau layanan formulir untuk pengiriman nyata.</p>
      </div>
      <form class="form" data-contact-form novalidate>
        <label>Nama
          <input type="text" name="name" required autocomplete="name" placeholder="Nama Anda">
        </label>
        <label>Email
          <input type="email" name="email" required autocomplete="email" placeholder="nama@contoh.com">
        </label>
        <label>Pesan
          <textarea name="message" required placeholder="Ceritakan singkat tentang proyek atau pertanyaan Anda"></textarea>
        </label>
        <button class="btn btn--primary" type="submit">%sKirim pesan</button>
        <p class="form__note muted" data-form-status role="status"></p>
      </form>
    </div>
    <aside>
      <div class="card" data-reveal>
        <div class="card__top">
          <span class="card__icon">%s</span>
          <span class="tag">Ketersediaan</span>
        </div>
        <h3 class="card__title">Terbuka untuk kolaborasi</h3>
        <p class="card__text">Saat ini menerima proyek rekayasa, tinjauan arsitektur, dan kolaborasi open source. Waktu balasan biasanya 1-2 hari kerja.</p>
        <div class="card__meta">
          <span><b>Zona waktu</b> WIB (UTC+7)</span>
          <span><b>Bahasa</b> ID / EN</span>
        </div>
      </div>
      <div class="card mt-4" data-reveal>
        <div class="card__top">
          <span class="card__icon">%s</span>
          <span class="tag">Kode</span>
        </div>
        <h3 class="card__title">Repositori</h3>
        <p class="card__text">Sebagian besar proyek tersedia sebagai repositori publik dengan dokumentasi dan catatan rilis.</p>
        <a class="card__link" href="projects.html">Telusuri katalog %s</a>
      </div>
    </aside>
  </div>
</section>
</main>
""" % (
        cards,
        icon("send"),
        icon("mail"),
        icon("github"),
        icon("arrow-right"),
    )
    page += search_dialog()
    page += footer()
    return page


def build_404():
    page = head("Halaman tidak ditemukan - Antono", "Halaman yang Anda cari tidak ditemukan.", "404.html")
    page += header("")
    page += """<main id="main">
<section class="section">
  <div class="shell" style="text-align:center; max-width: 40rem">
    <p class="eyebrow" style="justify-content:center">Error 404</p>
    <h1 class="section__title">Halaman tidak ditemukan</h1>
    <p class="section__lede">Tautan mungkin sudah berpindah atau tidak pernah ada. Coba kembali ke beranda atau telusuri katalog proyek.</p>
    <div class="hero__cta" style="justify-content:center">
      <a class="btn btn--primary" href="index.html">Kembali ke beranda</a>
      <a class="btn btn--ghost" href="projects.html">Lihat proyek</a>
    </div>
  </div>
</section>
</main>
"""
    page += footer()
    return page


def build_robots():
    return "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["url"]


def build_sitemap():
    # 404 is excluded: it is noindex, and listing it invites crawlers to fetch it.
    today = datetime.date.today().isoformat()
    urls = []
    for filename in PAGES:
        if filename == "404.html":
            continue
        loc = "%s/%s" % (SITE["url"], "" if filename == "index.html" else filename)
        priority = "1.0" if filename == "index.html" else "0.7"
        urls.append(
            "  <url>\n"
            "    <loc>%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            "    <changefreq>weekly</changefreq>\n"
            "    <priority>%s</priority>\n"
            "  </url>" % (esc(loc), today, priority)
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def build_manifest():
    return (
        json.dumps(
            {
                "name": "%s - %s" % (SITE["name"], SITE["tagline"]),
                "short_name": SITE["name"],
                "description": SITE["tagline"],
                "lang": "id",
                "dir": "ltr",
                "start_url": "./",
                "scope": "./",
                "display": "standalone",
                "background_color": "#0b1116",
                "theme_color": "#0b1116",
                "icons": [
                    {
                        "src": "assets/img/icon-192.png",
                        "sizes": "192x192",
                        "type": "image/png",
                        "purpose": "any",
                    },
                    {
                        "src": "assets/img/icon-512.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "any",
                    },
                    {
                        "src": "assets/img/icon-maskable-512.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "maskable",
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


PAGES = {
    "index.html": build_index,
    "projects.html": build_projects,
    "blog.html": build_blog,
    "resume.html": build_resume,
    "contacts.html": build_contacts,
    "404.html": build_404,
}


def main():
    for filename, builder in PAGES.items():
        (ROOT / filename).write_text(builder(), encoding="utf-8")
        print("wrote", filename)
    # Generated from the same PAGES map as the HTML so the two cannot drift.
    for filename, builder in (
        ("robots.txt", build_robots),
        ("sitemap.xml", build_sitemap),
        ("manifest.webmanifest", build_manifest),
    ):
        (ROOT / filename).write_text(builder(), encoding="utf-8")
        print("wrote", filename)


if __name__ == "__main__":
    main()
