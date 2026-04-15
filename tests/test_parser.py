from __future__ import annotations

from parser import parse_listings

SAMPLE_HTML = """
<html><body>
<h2 id="postings">Available For Rent</h2>
<div class="ap_ilmoitukset card-yhuone__container-2">

<div id="ap_ilmoitus__12345" class="card-ap-ilmoitus card-yhuone yhuoneistolista_single swiper-slide">
    <p><b class="card-ap-ilmoitus__title">Kandintie 3 D 14</b><br>Studio - 1H + kt, 24,5m<sup>2</sup><br>375€ / mo</p>
    <p class="card-ap-ilmoitus__ajankohta"><b>Leasing time</b><br>01.06.2026 - 31.08.2026</p>
    <p>Furnished apartment, walkable distance from the university. Quiet and peaceful neighbourhood. Free Sauna, washing machine.</p>
    <p class="card-ap-ilmoitus__contact">Piero Cianciotta<br>+358 44 9381660<br>cianciottapiero@gmail.com<br></p>
    <div class="social-share">
        <a class="card-ap-ilmoitus__directlink" href="https://www.psoas.fi/en/ap_ilmoitukset/vuokraan_asunnon-cianciotta/">27.03.26 09:47</a>
    </div>
</div>

<div id="ap_ilmoitus__67890" class="card-ap-ilmoitus card-yhuone yhuoneistolista_single swiper-slide">
    <p><b class="card-ap-ilmoitus__title">Yliopistokatu 2 B 316</b><br>Family - 2H + k, 46.00m<sup>2</sup><br>450€ / mo</p>
    <p class="card-ap-ilmoitus__ajankohta"><b>Leasing time</b><br>01.05.2026 - 20.06.2026</p>
    <p>I want to sublease a 2 room fully furnished family apartment that is neat and clean and in an excellent environment.</p>
    <p class="card-ap-ilmoitus__contact">Kowsar Alam<br>+358465527286<br>engr_kowsar@yahoo.com<br></p>
    <div class="social-share">
        <a class="card-ap-ilmoitus__directlink" href="https://www.psoas.fi/en/ap_ilmoitukset/vuokraan_asunnon-alam/">27.03.26 08:13</a>
    </div>
</div>

<div id="ap_ilmoitus__99999" class="card-ap-ilmoitus card-yhuone yhuoneistolista_single swiper-slide">
    <p><b class="card-ap-ilmoitus__title">Mannenkatu 2 A 419</b><br>Studio - 1H + k, 24.50m<sup>2</sup><br>525€ / mo</p>
    <p class="card-ap-ilmoitus__ajankohta"><b>Leasing time</b><br>04.05.2026 - 31.08.2026</p>
    <p>Vuokrataan siisti ja täysin kalustettu 24,5 m² yksiö Myllytullissa rauhallisella sijainnilla puistoalueen vieressä.</p>
    <p class="card-ap-ilmoitus__contact">Santeri Viinamäki<br>0406574555<br>santeri.viinamaki@gmail.com<br></p>
    <div class="social-share">
        <a class="card-ap-ilmoitus__directlink" href="https://www.psoas.fi/en/ap_ilmoitukset/vuokraan_asunnon-viinamaki/">08.04.26 10:27</a>
    </div>
</div>

</div>
</body></html>
"""


def test_parse_count():
    listings = parse_listings(SAMPLE_HTML)
    assert len(listings) == 3


def test_parse_address():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].address == "Kandintie 3 D 14"
    assert listings[1].address == "Yliopistokatu 2 B 316"


def test_parse_type():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].apartment_type == "Studio"
    assert listings[1].apartment_type == "Family"


def test_parse_rent():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].rent_eur == 375.0
    assert listings[1].rent_eur == 450.0
    assert listings[2].rent_eur == 525.0


def test_parse_size():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].size_m2 == 24.5
    assert listings[1].size_m2 == 46.0


def test_parse_leasing():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].leasing_start == "01.06.2026"
    assert listings[0].leasing_end == "31.08.2026"


def test_parse_contact():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].contact_name == "Piero Cianciotta"
    assert listings[0].phone == "+358 44 9381660"
    assert listings[0].email == "cianciottapiero@gmail.com"


def test_parse_posted_date():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].posted_date == "27.03.26 09:47"


def test_parse_listing_url():
    listings = parse_listings(SAMPLE_HTML)
    assert "cianciotta" in listings[0].listing_url


def test_parse_psoas_id():
    listings = parse_listings(SAMPLE_HTML)
    assert listings[0].psoas_id == "ap_ilmoitus__12345"
