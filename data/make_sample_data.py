"""Generate the synthetic sample dataset: python data/make_sample_data.py > data/sample_reviews.csv"""
import csv, random, sys

random.seed(7)

REVIEWS = {
    "en": ["My order arrived two weeks late and nobody answered my emails about it.",
           "Great quality, but the size guide on the website is really confusing.",
           "Customer service was friendly and solved my problem within a day.",
           "The product broke after one month and the refund process took forever."],
    "de": ["Meine Bestellung kam zwei Wochen zu spät und niemand hat auf meine E-Mails geantwortet.",
           "Gute Qualität, aber die Größentabelle auf der Webseite ist sehr verwirrend.",
           "Das Produkt ist nach einem Monat kaputt gegangen und die Rückerstattung dauert ewig."],
    "fr": ["Ma commande est arrivée avec deux semaines de retard et personne n'a répondu à mes messages.",
           "Très bonne qualité, mais le guide des tailles sur le site est vraiment difficile à comprendre.",
           "Le produit s'est cassé après un mois et le remboursement prend une éternité."],
    "nl": ["Mijn bestelling kwam twee weken te laat aan en niemand reageerde op mijn e-mails.",
           "Goede kwaliteit, maar de maattabel op de website is echt heel verwarrend."],
    "es": ["Mi pedido llegó con dos semanas de retraso y nadie respondió a mis correos.",
           "Muy buena calidad, pero la guía de tallas de la web es bastante confusa.",
           "El producto se rompió después de un mes y el reembolso está tardando muchísimo."],
    "pt": ["A minha encomenda chegou com duas semanas de atraso e ninguém respondeu aos meus emails.",
           "Boa qualidade, mas o guia de tamanhos no site é muito confuso e difícil de usar."],
    "sv": ["Min beställning kom två veckor för sent och ingen svarade på mina mejl.",
           "Bra kvalitet, men storleksguiden på hemsidan är väldigt förvirrande."],
}
REPLIES = {
    "en": "Thank you for your feedback. We are sorry for the trouble and our team will contact you shortly to help.",
    "de": "Vielen Dank für Ihr Feedback. Es tut uns leid und unser Team wird sich in Kürze bei Ihnen melden.",
    "fr": "Merci pour votre retour. Nous sommes désolés et notre équipe va vous contacter très rapidement.",
    "es": "Gracias por tu comentario. Lamentamos las molestias y nuestro equipo se pondrá en contacto contigo pronto.",
    "pt": "Obrigado pelo seu comentário. Lamentamos o incómodo e a nossa equipa vai entrar em contacto consigo em breve.",
    "sv": "Tack för din feedback. Vi beklagar besväret och vårt team kommer att kontakta dig inom kort.",
}

# company, domain, list of (customer_lang, reply_lang or None)
COMPANIES = [
    ("Nordlicht Outdoor", "nordlicht-outdoor.example",
     [("de", "en")] * 5 + [("fr", "en")] * 2 + [("nl", "en")] * 2 + [("en", "en")] * 3 + [("de", None)] * 2),
    ("Maison Verte Cosmetics", "maison-verte.example",
     [("fr", "fr")] * 4 + [("es", "fr")] * 3 + [("en", "fr")] * 1 + [("en", "en")] * 2 + [("es", None)]),
    ("Bergström Living", "bergstrom-living.example",
     [("sv", "sv")] * 5 + [("de", "de")] * 2 + [("de", "sv")] * 2 + [("en", "en")] * 3),
    ("Costa Azul Travel", "costa-azul-travel.example",
     [("pt", "pt")] * 5 + [("es", "es")] * 3 + [("en", "en")] * 3 + [("pt", None)] * 2),
    ("Lumen Software", "lumen-software.example",
     [("en", "en")] * 8 + [("en", None)] * 3),
    ("Helix Mobile", "helix-mobile.example",
     [("fr", "en")] * 2 + [("en", "en")] * 1 + [("fr", None)] * 4),
]

w = csv.writer(sys.stdout)
w.writerow(["company", "domain", "review_id", "review_date", "rating", "review_text", "reply_text"])
n = 0
for company, domain, pairs in COMPANIES:
    random.shuffle(pairs)
    for cl, rl in pairs:
        n += 1
        w.writerow([company, domain, f"R{n:04d}", f"2026-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
                    random.choice([1, 2, 2, 3, 4]), random.choice(REVIEWS[cl]), REPLIES[rl] if rl else ""])
