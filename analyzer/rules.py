from models.transaction import Transaction, TransactionCategory

RULE_SALARY = [
    "SALARY", "WAGE", "PAYROLL", "ЗАРПЛАТА", "З/П",
    "SALAIRE", "PAIE", "SALAIO",
]

RULE_RENT = [
    "RENT", "LOYER", "АРЕНДА", "RENTAL", "LOCATION",
]

RULE_BANK_FEES = [
    "FEE", "COMMISSION", "CHARGE", "BANK FEE", "MAINTENANCE",
    "SERVICE CHARGE", "КОМИССИЯ", "БАНК", "ОБСЛУЖИВАНИЕ",
    "NET INTEREST PAID", "INTEREST",
]

RULE_TRANSFER = [
    "TRANSFER", "REVOLUT", "WISE", "SEPA", "VIREMENT",
    "ПЕРЕВОД", "TRANSFERT", "TOP-UP",
    "INSTANT ACCESS SAVINGS",
]

RULE_REFUND = [
    "REFUND", "REMBOURSEMENT", "ВОЗВРАТ", "CASHBACK",
    "TERMINATION REFUND", "RENBOURSEMENT",
]

RULE_TAXES = [
    "TAX", "IMPÔT", "НАЛОГ", "TVA", "IRS", "FISCAL",
]

RULE_INSURANCE = [
    "INSURANCE", "ASSURANCE", "СТРАХОВАНИЕ",
]

RULE_SUBSCRIPTION = [
    "NETFLIX", "SPOTIFY", "SUBSCRIPTION", "ABONNEMENT",
    "ПОДПИСКА", "YOUTUBE", "DEEZER", "CANVA", "TELEGRAM",
    "BOARDGAMEARENA",
]

RULE_TRAVEL = [
    "HOTEL", "FLIGHT", "VOL", "TRAVEL", "AIRBNB", "BOOKING",
    "ПУТЕШЕСТВИЕ", "ОТЕЛЬ", "АВИАБИЛЕТЫ", "HÔTEL", "HOTEL",
    "AIR FRANCE", "RYANAIR", "EASYJET", "VIETNAM AIRLINES",
    "HOSTEL", "EXPEDIA", "SKYSCANNER", "TRIP.COM", "TRIPCOM",
    "LOTTE HOTELS", "LOTTE HOTEL",
    "BEIJING", "BEIJINGDAXING", "AIRPORT",
]

RULE_BUSINESS_INCOME = [
    "FACTURE", "INVOICE", "CLIENT PAYMENT", "CLIENT INVOICE",
    "СЧЕТ", "КЛИЕНТ", "ОПЛАТА ОТ КЛИЕНТА", "PAYMENT RECEIVED",
    "INCOMING PAYMENT", "PAYMENT FROM LBC", "LBC FRANCE",
]

RULE_FOOD = [
    "RESTAURANT", "CAFE", "SUPERMARKET", "MARCHÉ", "ALIMENTATION",
    "FOOD", "ЕДА", "ПРОДУКТЫ", "КАФЕ", "РЕСТОРАН",
    "MAGASIN U", "SUPER U", "CARREFOUR", "LECLERC", "AUCHAN",
    "MONOPRIX", "INTERMARCHÉ", "INTERMARCHE", "LIDL", "ALDI",
    "MCDONALD'S", "MCDONALDS", "BURGER KING", "KFC", "DOMINO'S",
    "BOULANGERIE", "PATISSERIE", "BOUCHERIE", "FROMAGERIE",
    "AU PAIN", "PAIN D'ANTAN", "MCDONALD", "TARTE TROPÉZIENNE",
    "GRAN CAFFE", "RESTAURANT MUSEE", "NEWNORMAL COFFEE",
    "OPETIT CAFE", "ABAY RESTAURANT", "KEOPINAI",
    "LUCKKIHALINMAT", "EUNHAENGGOL", "HYEONGJEO",
    "SSING SSING", "EMART24", "7-ELEVEN",
    "MAGNUM", "YANDEX.EDA", "YANDEX EDA",
    "MILLE ROUGE", "GS25", "CASH", "HEINEKEN",
    "TOO \"MERIEM FARM\"", "TOO \"NII EMIRMED\"",
    "MERIEM FARM", "NII EMIRMED",
    "MARIE BLACHERE", "GRAND FRAIS", "KARDESLER GIDA",
]

RULE_TRANSPORT = [
    "UBER", "TAXI", "TRANSPORT", "BOLT", "ТРАНСПОРТ", "МЕТРО",
    "GAS", "FUEL", "ESSENCE", "ТОПЛИВО",
    "VINCI AUTOROUTES", "AUTOROUTE", "AUTOROUTES", "AUTOPASS",
    "ESCOTA", "SANEF", "SAPN", "TOLL",
    "YANDEX GO", "YANDEX.GO", "JETPAY INDRIVE", "INDRIVE",
    "TOTALENERGIES", "TOTAL", "ESSO", "SHELL", "BP",
    "STATION", "PÉAGE", "PEAGE",
    "S3V MOTTARET", "FLIXBUS", "GRAB", "GO!",
    "JETPAY", "WHOOSH", "JP*WHOOSH",
    "ISTANBULKART", "MEGÈVE",
]

RULE_SHOPPING = [
    "AMAZON", "EBAY", "SHOP", "STORE", "ПОКУПКА",
    "ZALANDO", "ASOS", "H&M",
    "FNAC", "DECATHLON", "CASTORAMA", "LEROUX", "BRICOMARCHÉ",
    "WELDOM", "BUT", "IKEA", "CONFORAMA",
    "SEPHORA", "BEAUTÉ", "PRINK",
    "AUTODOC", "MAXICOFFEE",
    "LOPUS FRIPE", "SUMUP",
    "PG SUD DISTRIBUTION",
    "LEBONCOIN", "ACTION", "CULTURA",
    "LA TARTE", "MAGASIN", "IDEALP", "SMASHING", "LA POSTE",
]

RULE_HEALTH = [
    "PHARMACIE", "PHARMACY", "АПТЕКА", "DOCTOR", "MÉDECIN",
    "MEDECIN", "HÔPITAL", "HOPITAL", "CLINIC", "DENTIST",
    "OPTIQUE", "OPTICIEN", "SUNO", "EMIRMED", "MULTIDISCIPLINARY",
]

RULE_UTILITIES = [
    "EDF", "GDF", "ENGIE", "ELECTRICITÉ", "ELECTRICITE",
    "GAZ", "WATER", "EAU", "VEOLIA", "TOTAL ENERGIES",
    "INTERNET", "FREE", "ORANGE", "SFR", "BOUYGUES",
]

RULE_EDUCATION = [
    "SCHOOL", "ÉCOLE", "ECOLE", "UNIVERSITY", "UNIVERSITÉ",
    "UNIVERSITE", "COURSE", "COURS", "TRAINING", "FORMATION",
]

RULE_ENTERTAINMENT = [
    "CINEMA", "CONCERT", "THEATRE", "MUSÉE", "MUSEE",
    "MUSEUM", "OCÉANOGRAPHIQUE", "INSTITUT OCEANOG",
    "DEOKSUGUNG", "EX MACHINA",
]

RULE_INCOME_OTHER = [
    "APPLE PAY DEPOSIT", "PAYMENT FROM", "DEPOSIT",
]

RULES: list[tuple[list[str], TransactionCategory]] = [
    (RULE_SALARY, TransactionCategory.SALARY),
    (RULE_RENT, TransactionCategory.RENT),
    (RULE_BANK_FEES, TransactionCategory.BANK_FEES),
    (RULE_REFUND, TransactionCategory.REFUND),
    (RULE_TAXES, TransactionCategory.TAXES),
    (RULE_INSURANCE, TransactionCategory.INSURANCE),
    (RULE_SUBSCRIPTION, TransactionCategory.SUBSCRIPTION),
    (RULE_TRANSPORT, TransactionCategory.TRANSPORT),
    (RULE_FOOD, TransactionCategory.FOOD),
    (RULE_SHOPPING, TransactionCategory.SHOPPING),
    (RULE_HEALTH, TransactionCategory.HEALTH),
    (RULE_UTILITIES, TransactionCategory.UTILITIES),
    (RULE_EDUCATION, TransactionCategory.EDUCATION),
    (RULE_ENTERTAINMENT, TransactionCategory.ENTERTAINMENT),
    (RULE_TRAVEL, TransactionCategory.TRAVEL),
    (RULE_TRANSFER, TransactionCategory.TRANSFER),
    (RULE_BUSINESS_INCOME, TransactionCategory.BUSINESS_INCOME),
    (RULE_INCOME_OTHER, TransactionCategory.UNKNOWN_INCOME),
]


def apply_rules(transaction: Transaction) -> tuple[TransactionCategory, float]:
    desc_upper = transaction.description.upper()
    for keywords, category in RULES:
        for kw in keywords:
            if kw in desc_upper:
                return category, 0.85
    if transaction.type.value == "Income":
        return TransactionCategory.UNKNOWN_INCOME, 0.3
    return TransactionCategory.UNKNOWN_EXPENSE, 0.3
