# B1 — Benchmark v1 görev tanımı (worker agent için)

Amaç: persona yöntemlerini test edeceğimiz davranışsal benchmark katmanını kur. `experiments/`
olduğu gibi kalıyor (ad-hoc denemeler orada); benchmark `benchmark/b1/` altında yaşayacak.
Odak: olabildiğince çok oyun × persona-yöntemi × model kombinasyonunu TEK komutla
koşturabilmek. Skorlama katmanı sonraki iş — şimdilik temiz veri üretimi.

## Oyunlar (hepsi TEK-SEFERLİK, multi-turn yok)

Kalibrasyon (10): ölçtüğü parametre parantezde.
1. dictator (altruizm) — experiments/01'den uyarla
2. ultimatum-proposer (stratejik adillik) — experiments/02'den
3. ultimatum-responder (negatif misilleme) — experiments/02'den
4. trust-sender (güven) — experiments/03'ten
5. trust-returner (pozitif misilleme) — experiments/03'ten
6. public-goods + strategy method (işbirliği + koşullu-işbirlikçi tip teşhisi):
   normal katkı sorusu + "diğerleri ortalama X koyarsa sen ne koyarsın?" X∈{0,5,10,15,20}
7. holt-laury (risk): 10 satırlık standart fiyat listesi, güvenli/riskli lottery çiftleri
8. loss-gambles (loss aversion): "50-50 yazı-tura: +$X / −$5" kabul-ret serisi, X∈{2,4,5,6,8,10}
9. time-choices (sabır + present bias): "bugün $A vs 30 gün sonra $B" + "30 gün vs 60 gün" çiftleri
10. eleven-twenty (level-k): 11-20 arası para iste; rakipten tam 1 az istersen +$20 bonus

Holdout (4) — AYRI klasör `b1/holdout/`, persona tuning'i bunlara ASLA bakmaz:
11. pg-punishment (Fehr-Gächter tek-seferlik versiyonu: katkı sonrası ceza aşaması)
12. who-to-punish (Ertan-Page-Putterman: ceza kuralını oylama — tasarımı PDF'ten doğrula)
13. third-party-punishment (dictator + seyirci cezalandırabilir)
14. beauty-contest (0-100 arası sayı, ortalamanın 2/3'üne en yakın kazanır)

## Gömülü katmanlar (her oyuna)

- **Belief elicitation** (sadece 4, 6, 11): karardan önce ödüllü tahmin — "diğer oyuncuların
  ortalama ne yapacağını tahmin et, isabetli tahmine +$2".
- **Paraphrase ensemble**: her oyunun talimat metni ≥5 farklı wording (anlam aynı, yüzey farklı;
  1'i sayısal format değişikliği — payoff tablo vs düzyazı). Template sistemi kur, wording_id logla.
- **Tekrar**: her hücre ≥3 run (decision noise ölçümü bedavaya çıksın).

## Çıktı formatı (kritik)

Tek tidy tablo (parquet/csv): `model, persona_method, agent_id, game, role, condition,
wording_id, run, decision, belief, raw_response, timestamp, cost`.
Ajan kimliği persona-harness'tekiyle AYNI agent_id — aynı sanal kişi tüm oyunları oynayacak
(kişi-içi tutarlılık sonra analiz edilecek).

## Entegrasyon + disiplin

- Persona katmanı: mevcut 9-yöntem harness'ine tak (senin kurduğun yapı); yöntem seçimi flag'le.
- Modeller: experiments/lineup.py MODELS; koşudan önce price_audit.py; maliyet tahminini
  koşu BAŞINDA yazdır, $5/koşu üstünü onaysız başlatma.
- Tek giriş noktası: `python -m b1.run --games all --methods gps,twin2k --models lineup --n 50`
  gibi; kaldığı yerden devam edebilmeli (resume), yarım koşu veri kaybetmesin.
- Her oyunun insan referans değerleri (Mei/literatür stylized facts) `b1/references.yaml`'a
  şimdiden not düşülsün — skorlama sonra bunu okuyacak.
