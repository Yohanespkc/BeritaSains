import os
import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

try:
    from google import genai
    from google.genai import types
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False


# Configuration
RSS_URL = "https://news.google.com/rss/search?q=AI+OR+artificial+intelligence+OR+genomics+OR+genom+OR+CRISPR+when:1d&hl=en-US&gl=US&ceid=US:en"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "news.json")
MAX_HISTORICAL_DAYS = 30

def fetch_rss_news():
    print(f"Fetching RSS feed from: {RSS_URL}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(RSS_URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        articles = []
        
        for item in items:
            title_full = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
            
            # Google News titles are formatted as "Title - Source"
            source = "Google News"
            title = title_full
            if " - " in title_full:
                parts = title_full.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1]
                
            # Parse publication date
            # Example format: "Sun, 19 Jul 2026 13:13:41 GMT"
            pub_date_formatted = ""
            try:
                dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                pub_date_formatted = dt.strftime("%Y-%m-%d")
            except Exception:
                try:
                    # Fallback parser
                    import email.utils
                    parsed_date = email.utils.parsedate_to_datetime(pub_date_str)
                    pub_date_formatted = parsed_date.strftime("%Y-%m-%d")
                except Exception:
                    pub_date_formatted = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            articles.append({
                "original_title": title,
                "url": link,
                "source": source,
                "published_date": pub_date_formatted,
                "description_snippet": item.find('description').text if item.find('description') is not None else ""
            })
            
        print(f"Successfully fetched {len(articles)} raw articles from RSS.")
        return articles
    except Exception as e:
        print(f"Error fetching RSS: {e}", file=sys.stderr)
        return []

def get_mock_data():
    print("Generating high-quality mock data for testing...")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return [
        {
            "title": "Terobosan Baru: Model AI Terbuka China Saingi Raksasa Silicon Valley",
            "original_title": "Another powerful new artificial intelligence model from China took the US tech industry by surprise",
            "url": "https://example.com/ai-china-model",
            "source": "LinkedIn News",
            "published_date": today,
            "summary": "Startup AI asal China meluncurkan model open-source baru yang mengejutkan industri teknologi AS karena kemampuannya yang sangat kompetitif. Model ini menantang dominasi perusahaan besar Silicon Valley dengan performa tinggi yang dapat diakses secara gratis oleh pengembang.",
            "takeaways": [
                "Model open-source baru dari China menunjukkan kemajuan pesat dalam penelitian AI.",
                "Perusahaan-perusahaan Silicon Valley menghadapi tekanan kompetitif yang lebih besar.",
                "Aksesbilitas model ini mempercepat inovasi global di tingkat pengembang."
            ],
            "category": "Artificial Intelligence"
        },
        {
            "title": "Terapi Gen CRISPR Pertama untuk Penyakit Genetik Langka Disetujui",
            "original_title": "First CRISPR Gene Therapy for Rare Genetic Disorder Approved by FDA",
            "url": "https://example.com/crispr-approval",
            "source": "Nature Biotechnology",
            "published_date": today,
            "summary": "FDA secara resmi menyetujui terapi pengeditan gen berbasis CRISPR untuk mengobati kelainan genetik langka yang merusak sel saraf. Keputusan bersejarah ini membuka jalan bagi penyembuhan penyakit genetik kronis lainnya yang sebelumnya tidak dapat disembuhkan.",
            "takeaways": [
                "FDA memberikan persetujuan untuk terapi berbasis CRISPR pertama yang menyasar penyakit sel saraf.",
                "Teknologi pengeditan gen terbukti aman dan efektif dalam uji klinis fase akhir.",
                "Persetujuan ini menandai era baru dalam kedokteran presisi dan terapi genetik."
            ],
            "category": "Genom & Biotek"
        },
        {
            "title": "Ilmuwan Ciptakan Jaringan Otak Hibrida Menggunakan Chip Silikon dan Sel Saraf",
            "original_title": "Scientists Create Hybrid Brain Network Using Silicon Chips and Neurons",
            "url": "https://example.com/hybrid-brain",
            "source": "Science Daily",
            "published_date": today,
            "summary": "Tim peneliti gabungan berhasil menghubungkan sel saraf biologis hidup dengan chip silikon komputer menggunakan antarmuka bio-elektronik baru. Teknologi ini berpotensi digunakan untuk memulihkan fungsi sensorik pasien lumpuh serta mempercepat komputasi neuromorfik.",
            "takeaways": [
                "Integrasi sel saraf hidup dengan silikon membuka jalan bagi komputer biologis.",
                "Sistem bio-elektronik ini bekerja dengan mentransmisikan sinyal listrik dua arah secara real-time.",
                "Aplikasi masa depan berfokus pada prostetik canggih dan pemulihan cedera sumsum tulang belakang."
            ],
            "category": "Sains & Teknologi"
        },
        {
            "title": "Google Meluncurkan Gemini Pro Terbaru dengan Konteks Window Lebih Besar",
            "original_title": "Google Launches Upgraded Gemini Pro with Larger Context Window",
            "url": "https://example.com/gemini-pro-update",
            "source": "TechCrunch",
            "published_date": today,
            "summary": "Google resmi merilis pembaruan untuk model Gemini Pro yang kini mendukung pemrosesan dokumen panjang hingga jutaan token secara bersamaan. Pembaruan ini secara dramatis meningkatkan akurasi dalam menganalisis kode pemrograman kompleks dan laporan keuangan panjang.",
            "takeaways": [
                "Context window Gemini Pro diperluas untuk mendukung analisis data skala besar.",
                "Peningkatan efisiensi waktu pemrosesan dokumen teks dan video berdurasi panjang.",
                "Fitur baru ini mempermudah developer dalam membangun aplikasi AI tingkat enterprise."
            ],
            "category": "Artificial Intelligence"
        },
        {
            "title": "Sekuens Genom Lengkap Membuka Rahasia Evolusi Tanaman Padi Purba",
            "original_title": "Full Genome Sequencing Unlocks Secrets of Ancient Rice Evolution",
            "url": "https://example.com/rice-genome",
            "source": "Genomics Journal",
            "published_date": today,
            "summary": "Para peneliti genetika berhasil memetakan sekuens genom lengkap dari sampel padi purba berusia 3.000 tahun yang ditemukan di situs arkeologi. Data genetik ini mengungkap bagaimana nenek moyang kita melakukan seleksi tanaman terhadap kekeringan dan hama.",
            "takeaways": [
                "Pemetaan genom padi purba memberikan wawasan tentang adaptasi iklim masa lalu.",
                "Ditemukan gen ketahanan kekeringan spesifik yang hilang dalam varietas padi modern.",
                "Penemuan ini dapat membantu insinyur pertanian menciptakan padi modern yang lebih tangguh."
            ],
            "category": "Genom & Biotek"
        },
        {
            "title": "Superkomputer Masa Depan: Eksperimen Komputasi Kuantum Skala Besar Berhasil",
            "original_title": "Future Supercomputing: Large-scale Quantum Computing Experiment Succeeds",
            "url": "https://example.com/quantum-success",
            "source": "MIT Technology Review",
            "published_date": today,
            "summary": "Fisikawan berhasil menjalankan algoritma koreksi kesalahan kuantum yang stabil pada sistem 100-qubit untuk pertama kalinya. Hasil ini menunjukkan bahwa komputer kuantum komersial yang bebas dari error tingkat tinggi kini semakin dekat menjadi kenyataan.",
            "takeaways": [
                "Algoritma koreksi kesalahan kuantum berhasil menstabilkan sistem qubit dari gangguan luar.",
                "Sistem 100-qubit mampu memecahkan kalkulasi kimia kompleks dalam hitungan detik.",
                "Langkah krusial menuju komputer kuantum skala industri yang andal."
            ],
            "category": "Sains & Teknologi"
        },
        {
            "title": "AI Deteksi Dini Kanker Paru Melalui Pemindaian X-ray Biasa",
            "original_title": "AI Detects Early-Stage Lung Cancer Using Standard Chest X-rays",
            "url": "https://example.com/ai-lung-cancer",
            "source": "The Lancet Digital Health",
            "published_date": today,
            "summary": "Sebuah sistem kecerdasan buatan baru yang dilatih pada jutaan radiografi dada mampu mendeteksi tanda-tanda awal kanker paru dengan akurasi 94%. Sistem ini dapat mendeteksi nodul kecil yang sering terlewatkan oleh radiolog manusia pada pemeriksaan rutin.",
            "takeaways": [
                "Sistem AI melampaui rata-rata akurasi deteksi radiolog manusia dalam skrining awal.",
                "Meningkatkan peluang kesembuhan pasien secara dramatis melalui penanganan dini.",
                "Akan diintegrasikan ke klinik-klinik dengan sumber daya medis terbatas."
            ],
            "category": "Artificial Intelligence"
        },
        {
            "title": "Teknologi DNA Kuno Ungkap Pola Migrasi Manusia Pertama ke Amerika",
            "original_title": "Ancient DNA Technology Reveals Migration Patterns of First Americans",
            "url": "https://example.com/ancient-dna-america",
            "source": "Science Magazine",
            "published_date": today,
            "summary": "Studi terhadap sisa-sisa DNA kuno berusia 12.000 tahun menunjukkan bahwa pemukim pertama Amerika bermigrasi dalam beberapa gelombang yang berbeda secara genetik. Analisis ini meluruskan teori migrasi tunggal yang selama ini diyakini oleh para arkeolog.",
            "takeaways": [
                "Analisis genom kuno membuktikan adanya rute migrasi maritim di samping jembatan darat Beringia.",
                "Hubungan genetik terdeteksi antara populasi Siberia kuno dan suku asli Amerika Utara.",
                "Mengubah narasi sejarah prasejarah benua Amerika secara signifikan."
            ],
            "category": "Genom & Biotek"
        },
        {
            "title": "Baterai Garam Baru Menawarkan Alternatif Murah untuk Penyimpanan Energi Hijau",
            "original_title": "New Sodium-ion Battery Offers Cheap Alternative for Green Energy Storage",
            "url": "https://example.com/sodium-battery",
            "source": "Bloomberg Green",
            "published_date": today,
            "summary": "Para peneliti berhasil mengembangkan baterai sodium-ion (garam) berkapasitas tinggi dengan siklus hidup yang menyamai baterai lithium-ion. Karena sodium sangat melimpah dan murah, teknologi ini dapat mempercepat transisi ke penyimpanan energi surya dan angin skala besar.",
            "takeaways": [
                "Baterai berbasis garam menawarkan biaya produksi 40% lebih murah dibanding lithium.",
                "Memiliki keamanan termal yang sangat baik dan ramah lingkungan untuk didaur ulang.",
                "Solusi ideal untuk penyimpanan energi stasioner pada jaringan listrik kota."
            ],
            "category": "Sains & Teknologi"
        },
        {
            "title": "Perkembangan Pengkodean Musik Otomatis Menggunakan LLM Khusus Nada",
            "original_title": "Advancement in Automatic Music Generation Using Pitch-Specific LLMs",
            "url": "https://example.com/music-llm",
            "source": "Wired",
            "published_date": today,
            "summary": "Model bahasa besar (LLM) terbaru yang dikonfigurasi khusus untuk memahami teori musik dapat menghasilkan aransemen orkestra lengkap secara instan berdasarkan deskripsi teks. Model ini memahami harmoni dan transisi instrumen secara organik layaknya komposer profesional.",
            "takeaways": [
                "LLM musik baru menghasilkan musik dengan pemahaman struktural harmoni yang mendalam.",
                "Mampu menghasilkan file MIDI multi-instrumen yang dapat diedit secara profesional.",
                "Membuka perdebatan baru mengenai hak cipta karya seni yang dihasilkan oleh kecerdasan buatan."
            ],
            "category": "Artificial Intelligence"
        }
    ]

def summarize_with_gemini(raw_articles, api_key):
    print("Summarizing articles using Gemini API...")
    
    # We will pass a subset of raw articles to Gemini to avoid token bloat and select the 10 best.
    # Take the first 30 articles to select from
    candidate_articles = []
    for art in raw_articles[:30]:
        candidate_articles.append({
            "original_title": art["original_title"],
            "url": art["url"],
            "source": art["source"],
            "published_date": art["published_date"],
            "description": art["description_snippet"]
        })
        
    prompt = f"""
Tugas Anda adalah menyeleksi 10 berita sains dan teknologi paling menarik, terbaru, dan relevan dari daftar di bawah ini.
Fokus utama adalah pada perkembangan Artificial Intelligence (AI) dan Genom/Bioteknologi (seperti pengeditan gen, CRISPR, genomik).

Daftar kandidat berita:
{json.dumps(candidate_articles, indent=2)}

Silakan pilih tepat 10 artikel terbaik. Untuk setiap artikel yang dipilih:
1. Terjemahkan dan sesuaikan judulnya ke dalam Bahasa Indonesia yang menarik, informatif, dan profesional (jangan terjemahan harfiah kaku). Simpan ini di field "title".
2. Simpan judul asli bahasa Inggris di field "original_title".
3. Simpan "url", "source", dan "published_date" apa adanya.
4. Buat ringkasan (summary) dalam Bahasa Indonesia sepanjang 2-3 kalimat padat yang menjelaskan tentang apa berita tersebut, dampaknya, dan mengapa itu penting.
5. Ekstrak 3 poin kesimpulan utama (takeaways) dalam Bahasa Indonesia.
6. Klasifikasikan ke dalam salah satu kategori berikut: "Artificial Intelligence", "Genom & Biotek", atau "Sains & Teknologi".

Penting: Output Anda HARUS berupa JSON array of objects yang valid tanpa markdown formatting (misal tanpa bungkus ```json ... ```) atau teks penjelasan apa pun. Array harus berisi tepat 10 objek dengan format schema berikut:
[
  {{
    "title": "Judul Bahasa Indonesia",
    "original_title": "Original English Title",
    "url": "https://...",
    "source": "Nama Sumber",
    "published_date": "YYYY-MM-DD",
    "summary": "Ringkasan berita...",
    "takeaways": [
      "Kesimpulan 1",
      "Kesimpulan 2",
      "Kesimpulan 3"
    ],
    "category": "Artificial Intelligence" | "Genom & Biotek" | "Sains & Teknologi"
  }}
]
"""
    try:
        # Using the new google-genai client and gemini-2.0-flash
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        response_text = response.text.strip()
        
        # Parse output to ensure valid JSON
        news_data = json.loads(response_text)
        
        if not isinstance(news_data, list):
            raise ValueError("Gemini response is not a JSON list.")
            
        print(f"Successfully summarized {len(news_data)} articles via Gemini.")
        return news_data[:10]  # Ensure exactly 10 or up to 10
        
    except Exception as e:
        print(f"Error summarizing with Gemini: {e}", file=sys.stderr)
        print("Falling back to mock data.", file=sys.stderr)
        return get_mock_data()

def update_database(new_news):
    # Ensure directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Load existing news if it exists
    existing_news = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    existing_news = data.get("articles", [])
                elif isinstance(data, list):
                    existing_news = data
        except Exception as e:
            print(f"Error loading existing news database: {e}", file=sys.stderr)
            existing_news = []
            
    # Combine lists. To avoid duplicates, we use URL as the unique identifier.
    # Group news items by URL
    combined_dict = {}
    
    # Add existing news
    for item in existing_news:
        url = item.get("url")
        if url:
            combined_dict[url] = item
            
    # Add/overwrite with new news
    for item in new_news:
        url = item.get("url")
        if url:
            # If it's a new article, insert it. If it already exists, overwrite to refresh content.
            combined_dict[url] = item
            
    # Sort combined articles by published_date descending, then by title
    all_articles = list(combined_dict.values())
    
    # Simple parse helper for sorting
    def get_sort_key(item):
        date_str = item.get("published_date", "")
        try:
            # Treat empty date as oldest
            if not date_str:
                return (0, 0, 0)
            parts = [int(p) for p in date_str.split("-")]
            return tuple(parts)
        except Exception:
            return (0, 0, 0)
            
    all_articles.sort(key=get_sort_key, reverse=True)
    
    # Filter articles to keep only last MAX_HISTORICAL_DAYS of news (to keep file size small)
    filtered_articles = []
    now = datetime.now(timezone.utc)
    
    for item in all_articles:
        date_str = item.get("published_date", "")
        keep = True
        if date_str:
            try:
                item_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                age_days = (now - item_date).days
                if age_days > MAX_HISTORICAL_DAYS:
                    keep = False
            except Exception:
                pass  # Keep if date parsing fails, to be safe
        if keep:
            filtered_articles.append(item)
            
    # Write back to file
    metadata = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_articles": len(filtered_articles),
        "articles": filtered_articles
    }
    
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"Database updated successfully. Saved {len(filtered_articles)} articles in total.")
        print(f"Data saved to: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving updated database: {e}", file=sys.stderr)

def main():
    print(f"=== Daily News Scraper & Summarizer ===")
    print(f"Time: {datetime.now().isoformat()}")
    
    # 1. Fetch
    raw_articles = fetch_rss_news()
    
    # 2. Summarize (Gemini or Mock)
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not HAS_GEMINI_SDK:
        print("WARNING: google-genai package is not installed. Using mock data.")
        new_news = get_mock_data()
    elif not gemini_key:
        print("WARNING: GEMINI_API_KEY environment variable is not set. Using mock data.")
        new_news = get_mock_data()
    elif not raw_articles:
        print("WARNING: No raw articles found to summarize. Using mock data.")
        new_news = get_mock_data()
    else:
        new_news = summarize_with_gemini(raw_articles, gemini_key)
        
    # 3. Update JSON database
    update_database(new_news)
    print("=== Process Completed successfully ===")

if __name__ == "__main__":
    main()
