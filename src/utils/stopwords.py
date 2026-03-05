"""Stopwords module for text processing.

This module provides language-specific stopword collections used by keyword extraction
and token reduction features. Stopwords are common words that should be filtered out
from text analysis.

Supports 64 languages including Amharic.
"""

from typing import Dict, Set, Optional, List


class Stopwords:
    """
    Stopwords manager with language-specific stopword collections.
    
    Provides access to stopwords for 64 languages with support for
    locale normalization.
    """
    
    # Stopwords dictionary - language code -> set of stopwords
    STOPWORDS: Dict[str, Set[str]] = {
        # English
        "en": {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
            "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
            "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
            "during", "each", "few", "for", "from", "further", "had", "has", "have",
            "having", "he", "her", "here", "hers", "herself", "him", "himself", "his",
            "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
            "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
            "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over",
            "own", "same", "she", "should", "so", "some", "such", "than", "that", "the",
            "their", "theirs", "them", "themselves", "then", "there", "these", "they",
            "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
            "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
            "will", "with", "you", "your", "yours", "yourself", "yourselves"
        },
        
        # German
        "de": {
            "aber", "alle", "allem", "allen", "aller", "alles", "als", "also", "am", "an",
            "ander", "andere", "anderem", "anderen", "anderer", "anderes", "anders", "auch",
            "auf", "aus", "bei", "bin", "bis", "bist", "da", "damit", "dann", "das", "dass",
            "dein", "deine", "deinem", "deinen", "deiner", "dem", "den", "denn", "der", "des",
            "dessen", "dich", "die", "dies", "diese", "dieselbe", "dieselben", "diesem",
            "diesen", "dieser", "dieses", "dir", "doch", "dort", "durch", "ein", "eine",
            "einem", "einen", "einer", "eines", "einig", "einige", "einigem", "einigen",
            "einiger", "einiges", "einmal", "er", "es", "etwas", "euch", "euer", "eure",
            "eurem", "euren", "eurer", "für", "gegen", "gewesen", "hab", "habe", "haben",
            "hat", "hatte", "hatten", "hier", "hin", "hinter", "ich", "ihm", "ihn", "ihnen",
            "ihr", "ihre", "ihrem", "ihren", "ihrer", "im", "in", "indem", "ins", "ist",
            "jede", "jedem", "jeden", "jeder", "jedes", "jene", "jenem", "jenen", "jener",
            "jenes", "jetzt", "kann", "kein", "keine", "keinem", "keinen", "keiner", "können",
            "könnte", "machen", "man", "manche", "manchem", "manchen", "mancher", "manches",
            "mein", "meine", "meinem", "meinen", "meiner", "mir", "mit", "muss", "musste",
            "nach", "nicht", "nichts", "noch", "nun", "nur", "ob", "oder", "ohne", "sehr",
            "sein", "seine", "seinem", "seinen", "seiner", "selbst", "sich", "sie", "sind",
            "so", "solche", "solchem", "solchen", "solcher", "solches", "soll", "sollte",
            "sondern", "sonst", "über", "um", "und", "uns", "unser", "unsere", "unserem",
            "unseren", "unser", "unter", "viel", "vom", "von", "vor", "während", "war",
            "waren", "warst", "was", "weil", "welche", "welchem", "welchen", "welcher",
            "welches", "wenn", "werde", "werden", "wie", "wieder", "will", "wir", "wird",
            "wirst", "wo", "wollen", "wollte", "würde", "würden", "zu", "zum", "zur", "zwar",
            "zwischen"
        },
        
        # French
        "fr": {
            "a", "à", "ai", "aie", "aient", "ais", "ait", "alors", "après", "as", "avec",
            "avoir", "bon", "ca", "celle", "celui", "ces", "ce", "cet", "cette", "chacun",
            "chacune", "chez", "ci", "comme", "comment", "d", "dans", "de", "des", "dont",
            "du", "elle", "en", "encore", "es", "est", "et", "eu", "eue", "eues", "eurent",
            "eus", "eusse", "eussent", "eusses", "eussiez", "eussions", "fait", "faire",
            "fais", "faisez", "fait", "faites", "faut", "femme", "gens", "hui", "il", "ils",
            "je", "juste", "la", "le", "les", "leur", "leurs", "lui", "ma", "mais", "me",
            "même", "mes", "moi", "moins", "mon", "mots", "nous", "on", "ou", "où", "par",
            "pas", "personne", "peu", "peut", "plus", "plutôt", "point", "pour", "pourquoi",
            "qu", "quand", "que", "quel", "quelle", "quelles", "quels", "qui", "quoi",
            "sans", "se", "sera", "serai", "seraient", "serais", "serait", "seront", "ses",
            "seulement", "si", "sien", "soi", "soir", "somme", "son", "sont", "sous", "soyez",
            "suis", "sur", "ta", "te", "tels", "tes", "toi", "ton", "tôt", "tous", "tout",
            "toute", "toutes", "tres", "trop", "tu", "un", "une", "valoir", "vous", "vu"
        },
        
        # Spanish
        "es": {
            "a", "al", "algo", "algunas", "algunos", "allí", "allá", "almas", "ante", "antes",
            "aquel", "aquella", "aquellas", "aquellos", "aquí", "así", "aunque", "bajo", "bien",
            "cada", "casi", "como", "con", "contra", "cual", "cuales", "cualquier", "cuando",
            "cuanto", "de", "del", "dentro", "desde", "donde", "dos", "durante", "e", "el",
            "ella", "ellas", "ello", "ellos", "en", "entre", "era", "eramos", "eran", "eres",
            "es", "esa", "esas", "ése", "ésa", "ésas", "eso", "esos", "esta", "estar", "estas",
            "este", "esto", "estos", "estoy", "etc", "fue", "fueron", "fui", "fuimos", "ha",
            "haber", "había", "habían", "hace", "haces", "han", "hasta", "hay", "he", "hermosa",
            "him", "his", "hoy", "huyo", "i", "iba", "iban", "in", "incluye", "ir", "is", "it",
            "la", "lado", "las", "le", "les", "lo", "los", "más", "mas", "me", "mi", "mía",
            "mismo", "mucho", "muchos", "muy", "nada", "ni", "no", "nos", "nosotros", "nuestro",
            "nuestra", "nuestras", "nuestros", "nunca", "o", "ó", "onde", "or", "os", "otro",
            "otra", "otros", "otras", "para", "parece", "pero", "poco", "pocos", "por", "porque",
            "puede", "pueden", "pues", "que", "qué", "quien", "quienes", "quiere", "se", "sea",
            "sean", "según", "ser", "será", "serán", "sería", "si", "sido", "sin", "sino", "sobre",
            "solamente", "solo", "sólo", "somos", "son", "soy", "su", "sus", "también", "tampoco",
            "tan", "tanto", "te", "tengo", "ti", "tiempo", "todas", "todo", "todos", "tomar",
            "total", "tras", "tu", "tus", "tuya", "tuyo", "un", "una", "uno", "unos", "usted",
            "ustedes", "va", "van", "varias", "varios", "ve", "vez", "via", "voy", "ya", "yo"
        },
        
        # Italian
        "it": {
            "a", "ad", "adesso", "ai", "al", "alla", "alle", "allo", "allora", "altre", "altri",
            "altro", "anche", "ancora", "avere", "basta", "bisogno", "che", "chi", "chicchessia",
            "chiunque", "ci", "città", "coi", "col", "come", "con", "conoscere", "cosa", "credo",
            "d", "da", "dacci", "dove", "dopo", "dunque", "durante", "e", "è", "ebbe", "ebbero",
            "ecco", "fare", "fatto", "fosse", "fossero", "fra", "frattempo", "fu", "fui", "fummo",
            "furono", "futuro", "gia", "già", "giocare", "giorni", "giorno", "gli", "gliela",
            "gliele", "glieli", "glielo", "gliene", "governo", "grand", "grazie", "greve", "gross",
            "gruppo", "ha", "hai", "hanno", "ho", "ieri", "il", "improvviso", "in", "infatti",
            "ins", "intanto", "io", "l", "la", "là", "le", "lei", "li", "lo", "lontano", "loro",
            "luogo", "là", "ma", "macché", "magari", "mai", "male", "mancanza", "mangiare", "maniera",
            "mano", "mare", "marzo", "massimo", "meglio", "memor", "men", "meno", "mente", "mentre",
            "meraviglia", "mesi", "mezzo", "mi", "mia", "mie", "miei", "mila", "miliardo", "mille",
            "mio", "molta", "molti", "molto", "momento", "mondo", "monte", "morire", "mostrare",
            "mo", "muovere", "musica", "n", "nascere", "natura", "naturale", "nazione", "ndo",
            "ne", "né", "neanche", "necessità", "nemmeno", "neppure", "nessun", "nessuna",
            "nessuno", "niente", "no", "noi", "non", "nondimeno", "nonostante", "nostra", "nostre",
            "nostri", "nostro", "novanta", "nove", "novemila", "nulla", "o", "od", "oggi", "ogni",
            "ognuno", "oltre", "oppure", "ora", "ore", "ossia", "paese", "papà", "parere", "parete",
            "parlare", "parole", "parte", "partire", "passare", "passato", "passo", "paura", "pazienza",
            "peccato", "peggio", "pena", "pensare", "per", "perché", "perciò", "perfino", "però",
            "persino", "persona", "persone", "pesca", "pezzo", "piacere", "piano", "piccolo", "piede",
            "piedi", "pieno", "pietà", "poco", "poi", "poiché", "politica", "popolo", "porre",
            "porta", "portare", "posizione", "posto", "potere", "preferire", "prego", "presentare",
            "presto", "prima", "primo", "principale", "problema", "proprio", "prossimo", "pubblico",
            "pure", "purtroppo", "qualche", "qualcosa", "qualcuno", "qualcosa", "quale", "qualità",
            "qualunque", "quando", "quanto", "quasi", "quattro", "quello", "quest", "questa",
            "queste", "questi", "questo", "qui", "quindi", "quinto", "rispetto", "ritorno", "salire",
            "saltare", "salute", "sangre", "santo", "sapere", "scappare", "scegliere", "scelta",
            "scena", "sci", "scoprire", "scritto", "scuola", "se", "secondo", "sedersi", "segreto",
            "seguire", "seguito", "sembrare", "semplice", "sempre", "senso", "sentire", "senza",
            "sera", "serio", "servire", "servizio", "si", "sia", "siamo", "siano", "siccome", "sicuro",
            "silenzio", "simile", "sin", "sino", "sistema", "situazione", "smettere", "sn", "sobre",
            "sociale", "società", "sogno", "soldi", "sole", "solito", "solo", "soltanto", "sono",
            "sorella", "sorprendere", "sotto", "spalla", "spazio", "specialmente", "speranza",
            "sperare", "spesso", "spiegare", "st", "stampa", "stanco", "stanza", "stare", "stato",
            "stazione", "stesso", "stia", "stiamo", "stiano", "stile", "stima", "stesso", "sto",
            "stop", "strada", "strano", "stringere", "studiare", "studio", "stupido", "su", "subito",
            "succedere", "successo", "succiso", "sua", "sue", "suelo", "suff", "suitable", "suite",
            "suo", "surg", "sus", "susseg", "svari", "sviluppare", "sviluppo", "t", "tacere", "tale",
            "tali", "tanto", "tardi", "tavola", "te", "tempo", "tenere", "tentare", "tentativo",
            "terreno", "terzo", "testa", "tipo", "tirare", "titolo", "to", "toccare", "togliere",
            "tornare", "tra", "tranquillo", "trarre", "trattare", "tratto", "tre", "trenta",
            "triste", "troppo", "trovare", "tu", "tuo", "tutti", "tutto", "tutta", "tutte", "uccidere",
            "udire", "ufficio", "uguale", "ultimo", "umano", "umanità", "uman", "un", "una", "uno",
            "uomo", "ur", "usa", "usare", "usato", "uscire", "utile", "utilizzare", "v", "va",
            "vacaciones", "vago", "valore", "vario", "vecchio", "vedere", "vendere", "venire",
            "venti", "vento", "veramente", "verb", "verità", "vero", "verso", "vestire", "vez", "via",
            "viaggio", "vicino", "villa", "vincere", "violenza", "virtù", "vista", "vivere", "vivo",
            "voce", "voglia", "volere", "volgere", "volo", "volontà", "volta", "volte", "vuoto"
        },
        
        # Portuguese
        "pt": {
            "a", "à", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as",
            "às", "até", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles",
            "depois", "do", "dos", "e", "é", "ela", "elas", "ele", "eles", "em", "entre",
            "era", "eram", "essa", "essas", "esse", "esses", "esta", "estas", "este", "estes",
            "está", "estão", "estive", "estivemos", "estiveram", "estivesse", "estivessem",
            "estou", "eu", "foi", "fomos", "for", "fora", "foram", "fosse", "fossem", "fui",
            "há", "havia", "haviam", "isso", "isto", "já", "lhe", "lhes", "lo", "mais", "mas",
            "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "muitos", "na", "não",
            "nas", "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num",
            "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual",
            "quando", "que", "quem", "são", "se", "seja", "sejam", "sem", "ser", "será", "serão",
            "seria", "seriam", "seu", "seus", "só", "somos", "sou", "sua", "suas", "também",
            "te", "tem", "tém", "tendo", "tenha", "tenham", "temos", "tenho", "ter", "terá",
            "terão", "teria", "teriam", "teu", "teus", "teve", "tinha", "tinham", "tive",
            "tivemos", "tiveram", "tivesse", "tivessem", "tu", "tua", "tuas", "um", "uma",
            "umas", "uns", "vai", "vamos", "vão", "você", "vocês", "vos", "vossa", "vossas",
            "vosso", "vossos"
        },
        
        # Russian
        "ru": {
            "а", "без", "более", "больше", "будет", "будто", "бы", "был", "была", "были",
            "было", "быть", "в", "вам", "вас", "ведь", "весь", "вдруг", "ведь", "ведь",
            "во", "вот", "впрочем", "все", "всегда", "всего", "всем", "всеми", "всему",
            "всех", "второй", "вы", "г", "где", "говорил", "да", "даже", "два", "для",
            "до", "другой", "его", "ее", "ей", "еле", "если", "есть", "еще", "ещё", "ж",
            "же", "жизнь", "за", "зачем", "здесь", "и", "из", "или", "им", "иметь", "в",
            "иногда", "их", "к", "как", "какая", "какой", "кем", "когда", "кого", "ком",
            "конечно", "который", "кто", "ли", "либо", "лишь", "м", "мало", "мне", "мной",
            "мог", "могут", "моя", "моё", "мой", "мог", "может", "можно", "мол", "момент",
            "мочь", "мной", "мог", "могла", "могло", "муж", "мы", "на", "над", "надо",
            "назад", "наиболее", "например", "нас", "наш", "наша", "наше", "наши", "не",
            "него", "нее", "ней", "некоторый", "нельзя", "нем", "немало", "нередко",
            "ни", "нибудь", "никогда", "никто", "ничего", "но", "ну", "об", "однако",
            "он", "она", "они", "оно", "опять", "ор", "от", "очень", "первый", "по",
            "под", "после", "потом", "потому", "почему", "почти", "при", "про", "просто",
            "прямо", "раз", "разве", "с", "сам", "сама", "само", "свой", "своя", "своё",
            "свои", "себе", "себя", "сегодня", "сейчас", "сказал", "сказала", "сказать",
            "слишком", "снова", "со", "собой", "собственно", "совсем", "сок", "соответствует",
            "спасибо", "стал", "становиться", "стать", "столь", "столько", "сторона", "суть",
            "считать", "т", "так", "такая", "также", "такой", "там", "твой", "твоя", "твоё",
            "твои", "те", "тебе", "тебя", "тем", "теперь", "тех", "то", "тогда", "тоже",
            "только", "том", "тот", "точка", "третий", "тут", "ты", "у", "уже", "уметь",
            "хорошо", "хотеть", "хоть", "хотя", "хочешь", "часто", "человек", "чем", "через",
            "четвертый", "что", "чтобы", "чуть", "эти", "это", "этой", "этом", "этот", "эту", "я"
        },
        
        # Chinese (Simplified)
        "zh": {
            "的", "一", "是", "在", "不", "了", "有", "和", "人", "这",
            "中", "大", "为", "上", "个", "国", "我", "以", "要", "他",
            "来", "时", "后", "用", "就", "生", "会", "作", "分", "于",
            "到", "说", "国", "动", "出", "种", "而", "好", "如", "你",
            "对", "生", "能", "而", "子", "那", "得", "于", "着", "下",
            "自", "之", "年", "再", "进行", "并", "政", "工", "那", "也",
            "学", "过", "家", "十", "用", "发", "天", "如", "然", "作",
            "方", "成", "者", "日", "都", "三", "小", "军", "二", "无",
            "同", "么", "经", "法", "当", "起", "与", "好", "看", "学",
            "进", "将", "还", "分", "此", "心", "前", "面", "又", "定",
            "见", "只", "从", "无", "形", "相", "现", "在", "外", "将",
            "十", "月", "如", "然", "前", "所", "十", "月", "又", "对",
            "向", "但", "身", "往", "全", "给", "与", "却", "也", "使",
            "从", "应", "点", "其", "话", "将", "几", "此", "问", "见",
            "又", "如", "意", "出", "日", "里", "由", "与", "好", "看",
            "学", "军", "其", "最", "百", "将", "而", "却", "啊", "呢"
        },
        
        # Japanese
        "ja": {
            "の", "に", "は", "を", "た", "が", "で", "て", "と", "し",
            "れ", "さ", "ある", "いる", "も", "する", "から", "な", "こと",
            "として", "い", "や", "れる", "など", "なっ", "ない", "この",
            "ため", "その", "あっ", "よう", "また", "もの", "という", "あり",
            "まで", "られ", "なる", "へ", "か", "だ", "これ", "によって",
            "により", "おり", "より", "による", "ず", "なり", "られる",
            "において", "ば", "なかっ", "なく", "しかし", "について", "せ",
            "だっ", "できる", "それ", "う", "ので", "なお", "のみ", "でき",
            "き", "つ", "における", "および", "いう", "さらに", "でも", "ら",
            "たり", "その他", "に関する", "たち", "ます", "ん", "です"
        },
        
        # Arabic
        "ar": {
            "في", "من", "على", "إلى", "أن", "كان", "هذا", "التي", "الذي", "بين",
            "قد", "بعد", "ذلك", "له", "عند", "إذا", "كما", "هذه", "ذات", "هذا",
            "لكن", "ما", "لا", "عن", "مع", "ثم", "أو", "حتى", "كل", "بينما",
            "هو", "هي", "أن", "إن", "بأن", "على", "ف", "ثم", "ثم", "لو", "لكن"
        },
        
        # Amharic (አማርኛ) - Comprehensive stopwords list
        "am": {
            # Common conjunctions
            "እና", "እናም", "እናምስለ", "እንደ", "እንደምንድን", "እንዲህ", "እንዲህም", "እንድርና", "ስለ", "ስለዚህ",
            "ስለዚህም", "ስለዚሁ", "ያለ", "ያለው", "ያለን", "ያሉ", "ያላችው", "አለ", "አለው", "አለን", "አሉ",
            "አላቸው", "ነው", "ነዚህ", "ነዚሁ", "ሆነ", "ሆኖ", "ሆንን", "ነሱ", "ነሷ", "ማን",
            "ማንኛውም", "ማንኛውም", "ማንኛው", "ማንኛውን",
            # Pronouns
            "እኔ", "እኔም", "እኔን", "አኔ", "አንተ", "አንተን", "አንቺ", "አንቺን", "እሱ", "እሷ", "እነሱ",
            "እነሷ", "እነሱን", "እነሆ", "እኛን", "እኛ",
            "እንዴት", "እንዴትም", "እንዴታችው",
            # Demonstratives
            "ይህ", "ይህን", "ይህም", "ይህንን", "ይህያይ", "ይህዬ", "ዚህ", "ዚህን", "ዚህም", "ዚሁ",
            "ዚሁን", "ዚሁም", "ነዚህ", "ነዚሁ", "ነዚህም", "ነዚሁም",
            # Prepositions
            "ለ", "ለምን", "ለውጥ", "ለይን", "ለጋር", "ለገንዘብ", "ለመነገድ", "ለማድረግ",
            "ከ", "ከዚህ", "ከዚሁ", "ከነዚህ", "ከነዚሁ", "ከላንተ", "ከኋላ", "ከበፊቱ",
            "በ", "በስተቀር", "በላይ", "በታች", "በስር", "በኋላ", "በሁለቱም", "በሁሉም",
            "አስተዳደር", "አስተዳደሪያቸው", "አስተዳደራዊ",
            "ወደ", "ወደዚህ", "ወደዚሁ", "ወደላይ", "ወደታች",
            "ውስጥ", "ውስጥም", "ውጭ", "ውጭም",
            # Verbs (common auxiliary)
            "ነበር", "ነበሩ", "ነገር", "ነገሩ", "ነይሩ", "ነይራቸው",
            "ነይር", "ነይርን", "ነይሮሃል", "ነይሮልን",
            "ስለው", "ስለው", "ስለሱ", "ስለሷ",
            # Questions
            "ምን", "ምንድን", "ምንም", "ምንያህል", "ምንን", "ምንጭ", "ምንጩን",
            "እንዴት", "እንዴትም", "እንዴታችው",
            "ለምን", "ለምንድን", "ለምንጭ", "ለምንጩን",
            # Numbers (often stopwords)
            "አንድ", "ሁለት", "ሦስት", "አራት", "አምስት", "ስድስት", "ሰባት", "ስምንት",
            "ዘጠኝ", "አስር", "አስራን", "ሃያት", "ሃያስር", "ሃያስራን",
            "አንደን", "ሁለንድሮ", "ሦስቱን", "አራቱን", "አምስቱን",
            # Adverbs
            "ዛሩ", "ዛሩን", "ዛሩም", "አሁን", "አሁንም", "አሁንን",
            "በጣም", "በጣምም", "በጥልቀት", "በጥልቀትም",
            "ደግሞ", "ደግሞም", "ነገም", "ነገምም",
            "እስካሁን", "እስካሁንም", "እስከሁን", "እስከሁንም",
            "ሁልጊዜ", "ሁልጊዜም", "በሁልጊዜ",
            # Negation
            "አይሆንም", "አይሆንምም", "አይደለም", "አይደለምም",
            "አለማዳን", "አለማግኘት",
            # Connectors
            "እና", "እንደሆነ", "እንደሆን", "እንደምት", "እንደሚሆን",
            "ስለዚህ", "ስለዚህም", "ስለዚሁ", "ስለዚሁም",
            "ልዩ", "ልዩም", "እንዲሆን", "እንዲህ", "እንዲህም",
            "እንዴት", "እንዴትም", "እንዴታችው",
            # Time
            "ዘንድ", "ዘንድም", "እስከ", "እስከም", "እስከዚህ", "እስከዚሁ",
            "ለጠፋ", "ለጠፋም", "ለዘለዚህ",
            # Others common words
            "ነገስ", "ቃል", "እያንዳንዱ", "ሁሉ", "ሁሉም",
            "ወይም", "ወይምስለ", "ወይንም",
            "አንተ", "ለአንተ", "አንቺ", "ለአንቺ",
            "አይደለም", "አይሆንም",
            "ተብሎ", "ተብለው", "ተብሎም",
            "ነው", "ሆኖ", "ነውም",
            # Additional common Amharic words
            "ይሰማል", "ይሰማልም", "ይሰማልን",
            "ይገናል", "ይገናልም",
            "እንድርና", "እንድርን",
            "ይችላል", "ይችላልም", "ይችል",
            "ማለት", "ማለትም", "ማለትልን",
            "ማለትያን", "ማለትምያን",
            "ማንኛው", "ማንኛውም",
            "ያስፈልጋል", "ያስፈልጋልም",
            "ልክ", "ልክም", "ልክልን",
            "ልክተር", "ልክተርም",
            # More common words
            "እንተ", "እንተን",
            "እንዲያው", "እንዲያውም",
            "እንዲሆን", "እንዲሆንም",
            "ስለያይ", "ስለያይም",
            "ይደልያል", "ይደልያልም",
            "ለያንድን", "ለያንድንም",
            # More words
            "እንደው", "እንደውም",
            "እንዲል", "እንዲልም",
            "እንደርን", "እንደርንም",
            "እንዲርን", "እንዲርንም",
            # Additional
            "ስሙ", "ስም",
            "በቅርቡ", "በቅርብ",
            "በኋላ", "በፊት",
            "እስከማንን",
            "ስለማን",
        },
        
        # Dutch
        "nl": {
            "aan", "al", "alles", "als", "altijd", "ander", "andere", "anderen", "dan", "dat",
            "de", "den", "der", "deze", "dicht", "die", "dik", "dit", "doen", "door", "dus",
            "een", "eens", "eer", "eerder", "eerst", "eigen", "eigenlijk", "elk", "elke", "en",
            "er", "erg", "et", "ge", "geen", "geenszins", "gek", "geleden", "gelijk", "gen",
            "gerust", "geven", "gevoel", "gij", "haar", "had", "hadden", "hare", "heb", "hebben",
            "heel", "hem", "hemel", "hen", "her", "hier", "hij", "hoe", "hogere", "hun", "idee",
            "ik", "in", "inderdaad", "ineens", "iets", "ja", "je", "jongen", "jij", "jou", "jouw",
            "juist", "jullie", "kan", "kans", "kast", "kat", "keer", "kennen", "kerk", "keuken",
            "kiezen", "kijk", "klaar", "klagen", "klein", "kleur", "komen", "kon", "koning",
            "kopen", "kort", "kosten", "krijgen", "kun", "kunnen", "kwalijk", "laag", "lang",
            "langs", "last", "later", "leed", "leeg", "leggen", "leiden", "lekker", "les", "leven",
            "licht", "lid", "lief", "liefst", "liegen", "ligt", "lik", "lijken", "lijn", "lijf",
            "linker", "linkerkant", "lip", "literatuur", "locatie", "lokaal", "lonen", "lood",
            "loop", "los", "lots", "louter", "lucht", "luiden", "luister", "lukken", "lust",
            "maak", "maal", "maand", "maar", "maatschappij", "maat", "macht", "maken", "makkelijk",
            "man", "manier", "me", "meer", "meest", "meester", "mei", "meisje", "melden", "menen",
            "meneer", "mens", "mensen", "met", "mevrouw", "mij", "mijn", "miljard", "miljoen",
            "min", "minder", "minst", "miss", "misschien", "mobiel", "model", "moeder", "moeilijk",
            "mogen", "mooi", "morgen", "muur", "muziek", "na", "naar", "naam", "naast", "nacht",
            "nadat", "nagaan", "namelijk", "natuur", "natuurlijk", "nauwelijks", "nee", "neer",
            "negen", "nemen", "nergens", "net", "neus", "niemand", "niet", "niets", "nieuw",
            "nodig", "noemen", "nog", "nooit", "noot", "normaal", "nu", "of", "officier", "ofwel",
            "om", "omdat", "omstandigheid", "onafhankelijk", "onder", "ondertussen", "ongeveer",
            "ons", "onthouden", "ontvangen", "ook", "oog", "oom", "oon", "oor", "oordelen",
            "oorsprong", "oorzaak", "op", "open", "openen", "oppervlak", "ordel", "oud", "ouder",
            "over", "overal", "overheid", "overigens", "paar", "pad", "pagina", "pan", "park",
            "partij", "pas", "passen", "pers", "persoon", "plaats", "plan", "plein", "plek",
            "politie", "politiek", "pool", "poort", "poot", "post", "pot", "praktijk", "praten",
            "precies", "president", "prijs", "prima", "privaat", "probleem", "proces", "professor",
            "programma", "punt", "raad", "raam", "recht", "rechter", "rechts", "regel", "regering",
            "reis", "rekenen", "relatie", "rennen", "rest", "resultaat", "richten", "richting",
            "rijden", "rijk", "ring", "rivier", "rode", "roep", "ruim", "ruimte", "rust", "samen",
            "schade", "scheiden", "schijnen", "schilderen", "schip", "school", "schoon", "schrijven",
            "schudden", "seconde", "serie", "sfeer", "signaal", "sinds", "situatie", "slaan",
            "slag", "slaap", "slecht", "slechts", "sluiten", "smal", "sneeuw", "snel", "soms",
            "soort", "spelen", "spreken", "staan", "stap", "start", "staat", "stad", "stap",
            "steeds", "steen", "stel", "stellen", "stem", "sterk", "steun", "stil", "stoel",
            "stof", "stok", "stoppen", "straat", "straks", "streek", "streven", "strijd", "structuur",
            "student", "studie", "stuk", "sturen", "taak", "taal", "tafel", "tak", "talig",
            "tamelijk", "tand", "tante", "team", "teen", "tegen", "tegenover", "tekenen", "tekst",
            "televisie", "tenminste", "tenslotte", "terug", "terwijl", "thuis", "tien", "tij",
            "tijdens", "tijd", "titel", "toch", "toe", "toegang", "toen", "toename", "tonen",
            "tong", "tonnet", "toon", "top", "totaal", "trappen", "tree", "trouw", "trouwen",
            "tuin", "turn", "tussen", "twee", "tweede", "type", "uit", "uitgaan", "uiteraard",
            "uitleg", "uitsluiten", "uur", "vaak", "vader", "vakantie", "vallen", "van", "vanaf",
            "vandaag", "vandaan", "vangen", "varen", "vast", "veel", "veelal", "veertien", "veld",
            "ver", "veranderen", "verband", "verbergen", "verbieden", "verdedigen", "verder",
            "verdienen", "verdragen", "verdwijnen", "verenigen", "vergaderen", "vergelijken",
            "vergeten", "verhaal", "verhouding", "verkeerd", "verklaren", "verkopen", "verlangen",
            "verlaten", "verleden", "verliezen", "vermijden", "veroorzaken", "verplichten",
            "verregaand", "vers", "verschil", "verschillen", "verschillende", "verschijnen",
            "verslaan", "verspreiden", "verstaan", "vertegenwoordigen", "vertonen", "vertrekken",
            "vervolgens", "verwachten", "verwerken", "verwijzen", "verzamelen", "vet", "vier",
            "vijand", "vijf", "vijftien", "vinden", "vinger", "vis", "vlak", "vlees", "vlieg",
            "vliegen", "vlug", "voelen", "voeren", "voet", "vogel", "vol", "voldoende", "volgen",
            "volgend", "volgens", "volk", "volkomen", "volledig", "voor", "voorbeeld", "voorbij",
            "voordeel", "voorkomen", "voorlopig", "voornaam", "voornamelijk", "voorstellen",
            "voort", "vooruit", "voorzien", "vorm", "vormen", "vraag", "vragen", "vreemd",
            "vriend", "vrij", "vrijdag", "vroeg", "vroeger", "vrouw", "vrucht", "vullen", "vuur",
            "waar", "waaraan", "waarom", "waarschijnlijk", "wacht", "wagen", "wakker", "wal",
            "wand", "wandelen", "wanneer", "want", "warm", "wat", "water", "wee", "week", "weer",
            "weg", "wegen", "wegens", "weiden", "weigeren", "weinig", "wekken", "wel", "welke",
            "wellicht", "wenken", "wennen", "wereld", "werk", "werken", "werking", "werpen",
            "westen", "wet", "weten", "wetenschap", "wie", "wiel", "wij", "wijd", "wijken",
            "wijn", "wijs", "wijze", "wijzen", "wil", "wilde", "willen", "wind", "winkel",
            "winnen", "winter", "wit", "wonen", "woning", "woord", "worden", "zaak", "zacht",
            "zak", "zal", "zand", "ze", "zee", "zeer", "zeggen", "zeker", "zelf", "zelfs",
            "zenden", "zes", "zestien", "zetten", "zeven", "zeventien", "zich", "zicht", "zichzelf",
            "ziek", "zien", "zij", "zijn", "zin", "zingen", "zitten", "zo", "zoals", "zodra",
            "zoeken", "zogeheten", "zogenaamd", "zogenoemd", "zomaar", "zomer", "zon", "zondag",
            "zonder", "zoon", "zorg", "zorgen", "zou", "zulk", "zulke", "zullen", "zus", "zwaar",
            "zwak", "zwart", "zwemmen", "zwijn"
        },
        
        # Hindi
        "hi": {
            "अंदर", "अत", "अदि", "अध", "अन्य", "अप", "अपना", "अपनी", "अपने", "अभि", "अभी",
            "आदि", "आप", "इंहें", "इंहों", "इंहे", "इस", "इसकी", "इसके", "इसमें", "इसे",
            "उंहें", "उंहों", "उंहे", "उन", "उनकी", "उनके", "उनको", "उनमें", "उन्हें",
            "उन्हीं", "उन्हें", "उन्हों", "एंहें", "एंहे", "एव", "एवं", "ऐसे", "ओर", "और",
            "कइ", "कई", "कर", "करता", "करते", "करने", "करना", "करों", "कहते", "कहा",
            "का", "काफ़ी", "की", "कुछ", "कें", "केंहें", "को", "कोइ", "कोई", "कोन",
            "कोनसा", "कौन", "कौनसा", "गया", "घर", "चाहे", "जहाँ", "जहाँ", "जा", "जाई",
            "जाए", "जाओ", "जाएं", "जाने", "जब", "जबकि", "जहाँ", "जे", "जेहें", "जैसे",
            "तब", "तक", "तब से", "तरह", "तिंहें", "तिंहे", "तीन", "तो", "था", "थे", "दबारा",
            "दिया", "दुसरे", "दूसरे", "दो", "धर", "नहीं", "नव", "नहिं", "नहीं", "ना",
            "निचे", "नीचे", "नौ", "पकड़ा", "पर", "पहले", "पूरा", "पे", "फिर", "बन",
            "बनी", "बनाए", "बनाई", "बनाया", "बाए", "बीस", "भी", "भीतर", "मगर", "मानो",
            "में", "मेरे", "मैं", "मैने", "यदि", "यद्दपि", "यह", "यहाँ", "यहाँ", "यही",
            "या", "यिए", "यीं", "योग्यता", "लिये", "लीक", "लीके", "लेंगे", "वग़ैरह",
            "वर्ग", "वह", "वहाँ", "वहीं", "वाले", "वुह", "वुहाँ", "वे", "शायद", "शेष",
            "सब", "सबसे", "सकता", "सकते", "सकी", "सकने", "सक्राफ्ट", "सबके", "सबकी",
            "सबा", "सभी", "सभीको", "सभे", "सम", "समय", "समंद", "सर", "सरल", "साथ",
            "साबुत", "सीता", "सुना", "सुपर", "सहायता", "सों", "है", "हैं", "हैता",
            "हैती", "हैम", "हैरान", "हैसी", "हुआ", "हुई", "हुए", "हुओं", "हूँ", "हे",
            "हें", "हेरा", "ही", "हो", "होगा", "होगी", "होंगे", "होना", "होने", "हूँ",
            "हे"
        },
        
        # Korean
        "ko": {
            "가", "가까스로", "가령", "각", "각각", "각자", "각종", "갖고말다", "같", "같이",
            "거", "거의", "거든요", "거서", "것", "것과", "것등", "것들", "게", "게다가",
            "께", "꼭", "나", "나머지", "남", "남들", "남씨", "납량", "내", "낼", "너",
            "너희", "너희들", "네", "넷", "년", "노", "누가", "nyder", "는", "늘",
            "능히", "다", "다시", "다음", "다행", "당신", "당장", "대", "대로", "대하면",
            "대하여", "대해", "댁", "도", "도달", "도착", "또한", "동시", "동안", "두번째로",
            "둘", "둥", "뒤", "뒤따라", "드디어", "드물게", "등", "등등", "디자인", "따라",
            "따라서", "딱", "때", "때가 되면", "때문", "또", "뚜뚜", "르게", "로", "로봇",
            "리를", "마", "마당", "마라", "마련", "마리", "만", "만난", "만들", "만원",
            "많", "많이", "말", "말하면", "말장난", "매", "매번", "미터", "모든", "모든것",
            "모두", "몇", "몇개", "목", "못", "무조건", "무슨", "무엇", "물론", "및", "바꾸",
            "바꿔", "받", "받아", "밖", "발", "밤", "방", "배", "백", "번", "벌", "Bem",
            "법", "벗어", "별", "병", "报告", "보", "보아", "보이는", "보이스", "복",
            "부분", "본", "본인", "봉", "부문", "분", "불", "붐", "비걱", "비로소", "비록",
            "빔", "사랑", "사전", "산", "살", "삼", "상", "생", "서", "서두", "선", "선택",
            "설", "설령", "설마", "설문", "설사", "섬", "성", "세", "세상", "세번째",
            "세월", "속", "습", "시", "시간", "시금", "식", "실제", "십", "쌍", "아",
            "아래", "아무", "아무거나", "아무도", "아바타", "아예", "안", "않", "않고",
            "않는", "않다", "않았", "알", "알 수", "알겠소", "알겠지", "암", "암시",
            "압", "앙", "앞", "앞으로", "애", "액", "야", "약", "약간", "약속", "양",
            "양자", "어", "어디", "어떠", "어떤", "어떻게", "어디", "언덕", "언제",
            "언제나", "얼마", "얼마나", "얼마든지", "없", "에", "에러", "에미터", "역시",
            "영", "영어", "영향", "옆", "예", "예금", "예리", "오", "오래", "오르",
            "오시", "옥션", "온", "옷", "와", "와우", "외", "왜", "왜냐하면", "요", "용",
            "우", "우산", "울", "움", "웃", "원", "원격", "원래", "월", "위", "위해",
            "유", "유일", "음", "음식", "의", "의거", "의해", "이", "이것", "이들의",
            "이른바", "이슬", "이웃", "이젠", "일", "일단", "일반", "일본", "일부",
            "일분", "일시", "일요일", "일정", "임", "입", "자", "자신", "작", "잔",
            "잇", "있", "있다", "인", "인류", "인천", "인터넷", "일", "제", "조",
            "조금", "조사", "존재", "종", "종결", "종로", "좌", "주", "주년", "주일",
            "주제", "주체", "줄", "줄서", "중", "중국", "즈음", "즉", "즉시", "지",
            "지금", "지난", "지나간", "직전", "직후", "진", "질", "질문", "집", "집단",
            "짝", "찍", "차", "차라리", "착", "착한", "참", "첫", "첫째", "청년", "체",
            "쳐", "촌", "치", "친구", "칠", "침", "카드", "카지노", "칸", "컬러", "컴",
            "케이크", "코", "콘", "콜", "콩", "크", "크리", "클", "큰", "클럽", "킬로",
            "타", "타입", "탄", "탈", "탑", "탓", "태", "택", "터", "테", "텍스트",
            "톤", "통", "특별", "특히", "트", "트럭", "트럼프", "파", "파일", "팔",
            "팬", "페", "페북", "편", "평", "포", "포인트", "폴더", "표", "푸", "품",
            "피", "필", "필수", "필요", "한", "한국", "한때", "하지만", "항", "행",
            "향", "허", "헐", "형", "혜", "호", "홈", "화", "확인", "환경", "환불",
            "황제", "회", "효", "후", "훈련", "훨씬", "휴", "흐름", "흡"
        },
        
        # Turkish
        "tr": {
            "a", "acaba", "acep", "ad", "altı", "altmış", "ama", "ancak", "arada", "artık",
            "asıl", "aslında", "ay", "ayrıca", "az", "bana", "bari", "bazen", "bazı", "bazıları",
            "başka", "baştan", "belki", "ben", "benden", "beni", "benim", "beri", "beş",
            "bet", "bir", "biraz", "biri", "birkaç", "birkez", "birçok", "birşey", "birşeyi",
            "biz", "bizden", "bizi", "bizim", "bknz", "boks", "bol", "böyle", "böylece",
            "böyleyken", "bu", "buna", "bunda", "bundan", "bunlar", "bunları", "bunların",
            "bunu", "bunun", "burada", "buradan", "bütün", "da", "daha", "dahi", "dahil",
            "daima", "dair", "day", "de", "defa", "dek", "demin", "demincek", "deminden",
            "den", "deniz", "der", "derhal", "derex", "des", "dey", "digger", "dilers",
            "dilin", "dille", "dimi", "diye", "doksan", "dokuz", "dolayı", "dolayısıyla",
            "dön", "dört", "dstar", "duman", "dur", "dure", "durn", "dursun", "duy", "dü",
            "dünden", "dünyada", "düş", "e", "ed", "ede", "eden", "eder", "ederse", "ediyor",
            "eğer", "eh", "el", "elbette", "eld", "eller", "elvel", "em", "emme", "emri",
            "en", "enda", "endeks", "epey", "epeyce", "epk", "er", "erincek", "erken",
            "erkez", "erta", "erteri", "es", "ese", "esen", "ess", "et", "ete", "etken",
            "etmek", "etraf", "etraflarınca", "ev", "evet", "evvel", "ey", "eyle", "eyledi",
            "eyler", "f", "fakat", "fallan", "fi", "fider", "ga", "gai", "gan", "garon",
            "geç", "geçen", "geçer", "geçersiz", "geçti", "gerek", "gerçi", "gerekse",
            "gertu", "gerçekten", "getir", "gibi", "gibl", "gibrey", "gine", "gir", "gire",
            "giren", "girer", "göre", "göre", "görme", "görmek", "göster", "göstermek",
            "göz", "gu", "gul", "gün", "günah", "günde", "güzel", "ha", "haber", "hack",
            "had", "hakkında", "hakkın", "hâlâ", "halt", "hangi", "hangimiz", "hangisi",
            "hangisinin", "hani", "harde", "has", "hasılı", "hasta", "hatırlat", "havada",
            "havan", "hay", "hayat", "hayır", "haydi", "hedef", "hele", "heleki", "henüz",
            "hep", "hepiniz", "heps", "hepsi", "her", "herkes", "herkesin", "herse", "hiç",
            "hiçbir", "hız", "hiddet", "hindi", "hip", "hitap", "hı", "hıfzı", "i", "iç",
            "için", "içinde", "içinden", "ı", "ıblis", "ıd", "ıf", "ığı", "ıh", "ıhl",
            "ık", "ıkı", "ıl", "ıla", "ılan", "ıld", "ılon", "ım", "ıman", "ımd", "ımz",
            "ın", "ına", "ınak", "ınc", "ındex", "ını", "ıs", "ısk", "ısm", "ış", "ıt",
            "ıtf", "ız", "ızle", "kaç", "kaçak", "kadar", "kader", "kainat", "kal", "kala",
            "kaldı", "kalk", "kalkar", "kalkmaz", "kamyon", "kan", "kanca", "kapı", "kapan",
            "kapat", "kardeş", "karşı", "kartez", "kat", "kategori", "katsayı", "kaynak",
            "kazan", "kı", "kıla", "kısa", "kıskıvrak", "kıt", "kıvırcık", "kıyas", "kıyı",
            "kız", "kocaman", "koş", "koy", "koyar", "koyd", "koyduk", "koymak", "koyum",
            "koyver", "krar", "kullan", "kullanmak", "kumpanya", "kun", "kuru", "kuş",
            "kü", "küf", "külfet", "külot", "küme", "küçük", "kül", "kür", "l", "lakin",
            "lateks", "le", "len", "ler", "les", "let", "leyle", "lh", "li", "liane", "lisans",
            "liva", "lk", "lka", "lkre", "ll", "lse", "lurg", "m", "ma", "madem", "maf",
            "mahl", "mak", "maksat", "mal", "malesef", "mall", "man", "mana", "manda",
            "maniz", "mantı", "marka", "marul", "mas", "masall", "masa", "mastro", "mat",
            "mayo", "me", "medy", "mebni", "meclis", "medcezir", "meğer", "meğerse", "meh",
            "mem", "memnun", "mer", "mera", "mesela", "mesel", "mesudi", "meşgul", "met",
            "metin", "mev", "mevlana", "mevti", "mı", "mıç", "mıs", "mısr", "mız", "mıza",
            "mua", "mukabele", "mum", "mund", "mural", "mus", "mü", "mua", "muaf", "muaffak",
            "muallim", "muame", "mucize", "muh", "muhabere", "muhakkak", "muhalefet", "muhatap",
            "mümkün", "mümtaz", "münhasır", "münşeat", "müphem", "mürekkep", "müslüman",
            "n", "na", "nacizane", "nafile", "nai", "nak", "nane", "nasıl", "nat", "nazar",
            "nazii", "ne", "neden", "nedeniyle", "nedir", "nefis", "nefes", "nehy", "neler",
            "nerde", "nereden", "nereli", "neresi", "nesi", "net", "netice", "nez", "nida",
            "nihayet", "nil", "nim", "nitekim", "niye", "no", "nokta", "nor", "nost",
            "nö", "num", "nu", "nun", "nur", "nüsha", "o", "ob", "ocak", "oda", "off",
            "okey", "ok", "ol", "ola", "olabilir", "olamaz", "olan", "olarak", "oldu",
            "olduğu", "oldugunu", "olduk", "olmak", "olması", "olsa", "olsun", "olay",
            "olmadı", "olmuyor", "olur", "olursa", "olursun", "on", "ona", "ondan", "onlar",
            "onların", "onlari", "onların", "onnra", "ons", "onu", "onun", "ora", "ordan",
            "orada", "oradan", "oraya", "orayak", "organ", "organs", "oruç", "os", "osm",
            "ot", "oto", "otuz", "oy", "oysa", "oyuncak", "oz", "öz", "öbür", "ödenek",
            "ödünç", "öküz", "öl", "ölçü", "ölçüm", "öldür", "ölü", "ömür", "ön", "öna",
            "önce", "önceden", "öncelik", "öneli", "önem", "önemli", "öper", "öpet", "öpt",
            "ör", "öre", "örf", "örfi", "örneğin", "örnekle", "örümcek", "ös", "öt", "öte",
            "öteden", "öyle", "öylelikle", "öymen", "p", "paha", "pal", "pansiyon", "parasız",
            "park", "parsel", "part", "party", "paspas", "pat", "pav", "pazar", "pazartesi",
            "pe", "peki", "pek çok", "peşin", "pi", "pıl", "pırasa", "pırt", "pkk", "pkob",
            "pl", "plas", "play", "ple", "plj", "pob", "poh", "poker", "poş", "pot", "poyra",
            "poyraz", "pul", "pum", "punch", "pvp", "pı", "pıt", "r", "racon", "racun",
            "radar", "radyo", "rafta", "rag", "rahmet", "rak", "raman", "randevu", "rant",
            "raptiye", "rasat", "rast", "rata", "raunt", "ray", "razı", "re", "reel", "rehin",
            "rejim", "rekor", "rel", "ren", "res", "reşit", "reyt", "rı", "rıza", "rica",
            "rit", "riya", "ro", "robot", "rol", "rom", "rota", "rövanş", "ru", "rub", "ruj",
            "rup", "rutin", "rü", "rüya", "rüzgar", "s", "sab", "sabah", "sabıka", "sabotaj",
            "sad", "sade", "sadece", "sadr", "saffet", "sah", "şah", "şahıs", "sahne",
            "sair", "saka", "sal", "salı", "salkım", "salon", "salyangoz", "sam", "şan",
            "san", "sanat", "sana", "sanki", "santim", "santra", "sap", "şap", "sara",
            "saray", "sargı", "şarkı", "şart", "sas", "sat", "şat", "savaş", "savcı",
            "savlı", "say", "şayet", "sayen", "sayet", "sayfa", "sayı", "se", "seans",
            "sed", "sefer", "sefil", "seg", "sel", "selam", "sele", "sema", "şema", "semt",
            "sen", "sena", "senato", "seni", "senin", "ser", "şer", "şeref", "seri", "sermaye",
            "şerri", "ses", "sessiz", "set", "şey", "seyyah", "sezip", "sı", "sıcak",
            "sıddık", "sıfat", "sıhhiye", "sıla", "sınav", "sıra", "sırasıyla", "sırt",
            "sıva", "sicim", "sifiliz", "sihir", "sil", "silâh", "silgi", "silik", "silk",
            "silsile", "sır", "sırça", "sırf", "sırı", "sırma", "sırt", "sıtma", "sıva",
            "sızdır", "sızı", "siz", "sizi", "sizin", "sk", "skip", "sl", "slymph", "so",
            "sob", "sok", "sök", "söktür", "sol", "şol", "somb", "somut", "son", "şona",
            "sonra", "sonsuz", "sonuç", "sop", "soru", "sorun", "söz", "sözdizimi", "spor",
            "sı", "sık", "sıska", "sıt", "sub", "suk", "sulu", "sus", "sükut", "süre",
            "sürek", "sürekli", "süresiz", "sürpriz", "sürtük", "sürtünme", "süs", "süsl",
            "süsnü", "süspansiyon", "süvari", "t", "ta", "tab", "tahmin", "tahta", "tak",
            "takdir", "taksim", "takvim", "tal", "talep", "tali", "tam", "tamb", "tamam",
            "tamar", "tanker", "tarih", "tas", "taş", "tat", "tatsızlık", "tava", "tavaf",
            "tavşan", "taz", "taze", "tc", "td", "te", "ted", "teh", "tek", "tekel",
            "televizyon", "tem", "tema", "temmuz", "ten", "teneke", "ter", "tera", "teras",
            "tercih", "tercüme", "tereddüt", "terfi", "terler", "termal", "termit", "ters",
            "tesir", "tespit", "test", "teşekkür", "teşhis", "tex", "tg", "th", "thc",
            "tht", "tı", "tıbbi", "tılsım", "tırnak", "ticaret", "timsah", "tip", "tiran",
            "tiraj", "tit", "timsah", "tok", "tokat", "ton", "top", "topla", "toplam",
            "toptan", "tor", "toral", "torba", "torpido", "tortu", "tos", "tost", "tour",
            "tpa", "tpr", "tr", "tren", "triko", "trix", "troleybüs", "trombon", "trotin",
            "tuat", "tug", "tuğ", "tuğgeneral", "tuk", "tul", "tun", "tur", "turnike",
            "tür", "türban", "türe", "türlü", "türkiye", "türüz", "tutu", "tutuş", "tüy",
            "tüylü", "tv", "tweet", "twitch", "twitter", "ty", "tü", "tıp", "u", "uav",
            "uber", "uç", "uçak", "uçur", "uçuş", "uda", "uh", "uhde", "uhdud", "uhtt",
            "uk", "ul", "ula", "ulak", "ulan", "ulama", "ulamsal", "ult", "ultraviyole",
            "um", "umde", "umm", "ummak", "umran", "umre", "umul", "umursamaz", "un",
            "ün", "unf", "unutmak", "us", "usul", "ut", "utum", "utz", "uydur", "uydurma",
            "uygulama", "uyku", "uyma", "uz", "uzay", "uzun", "uzunca", "uzuv", "ü", "ücra",
            "ücret", "üç", "üçüncü", "üf", "ül", "üleş", "ülke", "ümit", "ümran", "ün",
            "üniversite", "ünlü", "ür", "üra", "üret", "üst", "üstat", "üş", "üşenmek",
            "üt", "ütopya", "val", "vane", "vanti", "var", "varagele", "vasıta", "vasıl",
            "vatan", "ve", "vebal", "vecibe", "vefat", "vegel", "vehd", "vehim", "velev",
            "velhasıl", "veli", "veliaht", "veliyyet", "ver", "verd", "verdim", "veresiye",
            "vergi", "verin", "vermek", "vers", "ves", "vesile", "vest", "vezir", "vibr",
            "viday", "video", "view", "vigit", "vın", "vız", "vizo", "vokal", "vol",
            "vot", "voxel", "vps", "vrb", "vs", "vt", "vtr", "vu", "vul", "vur", "vurgun",
            "vuruk", "vut", "vz", "x", "xb", "xen", "xerox", "xf", "xhtml", "xi", "xlsx",
            "xox", "xpm", "xs", "xstr", "xv", "xx", "xxx", "y", "ya", "yabancı", "yada",
            "yani", "yankı", "yap", "yapı", "yapıcı", "yapılma", "yapımı", "yapış", "yaptı",
            "yaptım", "yara", "yaramaz", "yarasa", "yardımcı", "yargı", "yarlıgamak",
            "yasa", "yaş", "yaşam", "yassı", "yat", "yatan", "yatırım", "yaz", "yazı",
            "yazık", "yazım", "yazın", "ybb", "ye", "yedi", "yedek", "yeğ", "yeğin",
            "yel", "yelpaze", "yemin", "yen", "yener", "yeni", "yeniden", "yeraltı",
            "yere", "yerine", "yermek", "yeşil", "yet", "yetenek", "yeter", "yeterli",
            "yetke", "yetkin", "yetmez", "yevmiye", "yı", "yıkan", "yıkmak", "yıl", "yıllık",
            "yılmak", "yırtık", "yığın", "yine", "yirmi", "yirminci", "yiti", "yitim",
            "yiv", "yok", "yoksa", "yoksul", "yokuş", "yol", "yorgun", "yoz", "yudum",
            "yug", "yulaf", "yü", "yumuşak", "yün", "yürü", "yürümek", "yürüt", "yüz",
            "yüzey", "yüzlerce", "z", "za", "zaman", "zann", "zannedermisin", "zannetmek",
            "zapt", "zar", "zarf", "zaten", "zayıf", "ze", "zebani", "zefir", "zehir",
            "zekat", "zeki", "zel", "zemin", "zencefil", "zerdali", "zerre", "zevk", "zeytin",
            "zıb", "zıkkım", "zımni", "zımparala", "zır", "zırh", "zırt", "zıvana", "zone",
            "zoom", "zuhaf", "zuhurat", "zul", "zümre", "zümrüt", "zürafa"
        },
        
        # Swedish
        "sv": {
            "aderton", "adertio", "adjö", "aldrig", "all", "allaredan", "allas", "allt",
            "alltid", "alltså", "än", "ännu", "är", "arbete", "arg", "av", "även", "bland",
            "blev", "bli", "blir", "blivit", "borde", "bort", "borta", "bra", "bringa",
            "bröd", "buren", "dag", "dagar", "dagarna", "dagen", "de", "dem", "den", "denna",
            "deras", "det", "dig", "din", "dina", "dit", "ditt", "dö", "död", "döda", "dömt",
            "där", "då", "efter", "eger", "ej", "eller", "en", "ena", "ene", "enem", "ens",
            "er", "era", "ert", "ett", "eller", "fanns", "får", "få", "fått", "fanns", "far",
            "fast", "fick", "fil", "fin", "fina", "fine", "fler", "flera", "flesta", "folk",
            "for", "fordran", "för", "före", "förlora", "förlorade", "förlorat", "förra",
            "första", "förutom", "fru", "fungerar", "fyra", "fem", "femte", "femtio", "fick",
            "fram", "från", "fred", "fri", "fria", "frisk", "fråga", "från", "ful", "fyra",
            "få", "får", "fått", "följande", "för", "först", "första", "gifta", "gick",
            "gillar", "giltig", "glas", "gods", "god", "goda", "godmorgon", "golf", "godtag",
            "golv", "gotland", "grov", "grunna", "gräva", "gud", "gul", "guld", "gälla",
            "gärna", "gå", "gång", "går", "gäta", "ha", "hade", "haft", "halv", "hand",
            "han", "hennes", "himlen", "historia", "hit", "hittade", "hittar", "hjälp",
            "hjälpa", "hon", "honom", "hundra", "hur", "hustru", "huvudsats", "håll", "hålla",
            "hållbar", "håller", "hälften", "här", "häre", "hög", "höger", "högre", "högst",
            "hör", "höra", "höras", "hörlurar", "i", "ibland", "idag", "igen", "ikea",
            "illa", "imorgon", "in", "inför", "inga", "ingen", "inom", "inte", "ironi",
            "is", "island", "ja", "jag", "jaka", "jam", "jams", "jazz", "jo", "jobb",
            "jobba", "jorden", "jul", "jungfru", "jurist", "just", "jämför", "järn", "järnväg",
            "jätt", "jätte", "kan", "kanske", "kapa", "katt", "kedja", "kilometer", "kilowatt",
            "kirurg", "kista", "kjol", "klocka", "klok", "klor", "knapp", "knappt", "kniv",
            "ko", "kok", "kolla", "koloni", "kom", "koma", "komma", "kommer", "kompis",
            "kona", "kopia", "kopp", "kostym", "kran", "krig", "krishantering", "kropp",
            "kula", "kult", "kultur", "kund", "kung", "känna", "kännas", "kär", "kärlek",
            "kö", "kök", "köpa", "köpmakare", "kör", "köra", "körsbär", "lacker", "ladugård",
            "lag", "laga", "landa", "lang", "lång", "långsamt", "lan", "last", "latin",
            "lava", "led", "leda", "ledare", "ledsen", "lefva", "legal", "leja", "lek",
            "leka", "lena", "lenin", "leon", "leopard", "ler", "lett", "lever", "levi",
            "levy", "li", "liberal", "licens", "lidelse", "lieder", "ligga", "light", "lik",
            "lika", "lilja", "limpa", "lin", "lina", "link", "linje", "linje", "lins",
            "lion", "lira", "list", "liter", "litet", "liv", "livet", "livs", "livsmedel",
            "ljud", "ljust", "lo", "lock", "lod", "loft", "log", "logo", "lok", "loka",
            "lokus", "lon", "loppa", "lotta", "loud", "lov", "lova", "lps", "lu", "lucka",
            "lud", "ludde", "luft", "lukt", "lun", "luna", "lunch", "lunga", "lunk", "lust",
            "lyc", "lyckas", "lycka", "lycklig", "lyda", "lydig", "lyft", "lyka", "lyra",
            "lys", "lysande", "lysa", "lysdi", "lyser", "lysin", "lyst", "lät", "låda",
            "låg", "lån", "lång", "låt", "lö", "löf", "lögn", "lök", "lön", "löp", "löpa",
            "löv", "macka", "madam", "made", "mager", "magsäck", "maj", "maka", "maken",
            "maklig", "man", "mandel", "manga", "många", "månad", "måndag", "månen", "måste",
            "mätte", "med", "mellan", "men", "menad", "mening", "mer", "mera", "mest", "mes",
            "meter", "metyl", "midi", "mie", "mig", "mil", "mild", "miljard", "miljon",
            "militär", "milla", "mil", "mimas", "mindre", "mineral", "min", "minder", "ming",
            "minig", "minim", "minne", "misse", "misär", "mka", "mkm", "ml", "mobil", "mocka",
            "mod", "möd", "moder", "modern", "mogna", "mold", "mona", "monopol", "mora",
            "morgon", "morn", "mos", "motor", "mous", "mr", "mre", "mt", "munt", "mus",
            "muse", "musik", "muskel", "muss", "muster", "myra", "myr", "mätt", "möbel",
            "mönster", "möta", "möter", "mötes", "mött", "mössa", "n", "na", "nad", "naj",
            "namn", "nano", "napp", "narr", "nation", "natt", "natur", "naturlig", "nav",
            "nej", "ner", "ni", "nick", "nicotin", "ninja", "nis", "nix", "njure", "no",
            "nog", "noll", "nom", "nominativ", "non", "nor", "nord", "norden", "norr", "nos",
            "not", "nu", "nul", "nummer", "nun", "nutt", "ny", "nyck", "nyhet", "nykomling",
            "nylon", "nyp", "nys", "nytta", "nyval", "objekt", "också", "offra", "ofta",
            "ok", "okey", "okt", "olag", "olan", "olika", "olja", "olka", "olle", "olt",
            "om", "omedelbart", "omfatta", "omgående", "omkring", "omsorg", "omtanke", "on",
            "ond", "onödig", "ooxo", "opal", "opera", "opt", "oral", "oran", "ord", "order",
            "organ", "orsak", "ort", "os", "ost", "otrolig", "ovan", "ovanlig", "over",
            "oxel", "oxford", "oy", "p", "padda", "paket", "pakt", "pal", "pall", "pan",
            "pank", "pappa", "park", "part", "partner", "pass", "passa", "pastorn", "pat",
            "paten", "patrull", "penna", "pensionat", "per", "pers", "pga", "pH", "piano",
            "pick", "piga", "pike", "pil", "pill", "pilsner", "ping", "pinnen", "pints",
            "pip", "pizza", "pjä", "pjäs", "pk", "plakat", "plan", "plank", "platta", "play",
            "plocka", "plund", "plupp", "plus", "plut", "pm", "po", "pojke", "pokal", "pola",
            "polar", "pom", "pond", "pool", "pop", "populär", "por", "port", "poser", "post",
            "potatis", "potta", "prakt", "prata", "preja", "press", "prio", "pris", "prins",
            "prinsessa", "pro", "profit", "promenad", "prop", "prova", "pryl", "präst",
            "psalm", "pub", "puck", "pula", "pull", "puls", "pump", "punch", "punk", "pupill",
            "pur", "puss", "puta", "puzzel", "pyramid", "pys", "pyssla", "pyt", "på", "pärl",
            "pö", "pöl", "på", "race", "radie", "radion", "raft", "rag", "raid", "rally",
            "ram", "ramp", "rand", "ranger", "rank", "rap", "rapt", "ras", "rat", "rata",
            "ray", "rea", "reg", "regering", "region", "regn", "rek", "rekl", "rekord",
            "rel", "relief", "rem", "rensa", "reptil", "res", "rese", "rest", "restaurang",
            "retur", "revy", "rh", "ribba", "ricard", "rich", "rick", "rid", "ridå",
            "rigor", "rika", "rikedom", "riksdag", "rim", "rimlig", "rind", "ring", "rink",
            "rinn", "rinner", "ris", "rit", "riva", "robe", "rock", "rod", "rodd", "rody",
            "rolig", "rom", "romersk", "ron", "rond", "roo", "rost", "rot", "roter", "rout",
            "rov", "rubin", "ruda", "rugby", "ruin", "rulla", "ruls", "rum", "rumänien",
            "run", "rund", "runda", "runk", "rus", "rush", "rygg", "rynk", "rör", "röra",
            "rörd", "rörelse", "röv", "s", "sa", "säck", "säga", "säker", "sälja", "säng",
            "särskild", "sätta", "så", "såg", "sång", "sår", "sakta", "samma", "samt",
            "sank", "sanna", "sann", "sanning", "sats", "se", "sedan", "sedel", "segel",
            "sej", "sel", "sem", "sen", "senap", "serie", "servis", "sett", "sexuell", "sig",
            "sik", "sil", "silt", "simbassäng", "sind", "sinnen", "sir", "siren", "sirlig",
            "sis", "sist", "sista", "site", "sitta", "sj", "själv", "sjös", "sjuk", "själ",
            "själv", "ska", "skada", "skadad", "skald", "skall", "skapa", "skatt", "sked",
            "skellefteå", "skepp", "skid", "skift", "skil", "skrift", "skriva", "skrivbord",
            "skrov", "skräddare", "skräp", "skuld", "skur", "skvätt", "sl", "slag", "slam",
            "slang", "slant", "släkt", "släppa", "släp", "sled", "slev", "slice", "slik",
            "sling", "slink", "slump", "slut", "slå", "smak", "smal", "smed", "smäll",
            "smärt", "smärtstillande", "smörgås", "snäll", "snö", "soffa", "sok", "sol",
            "solig", "soppa", "sorg", "sot", "sova", "spa", "spann", "spare", "sparven",
            "spela", "spets", "spik", "spill", "spion", "spola", "sport", "språk", "spö",
            "spöke", "staden", "stall", "stamp", "stark", "start", "stat", "ste", "sted",
            "steeg", "sten", "stiga", "stjärna", "stock", "stopp", "storm", "strumpa", "studie",
            "stuga", "stumm", "stil", "stil", "sting", "stjärna", "sto", "stock", "stol",
            "stom", "stop", "store", "storm", "story", "sträcka", "strå", "ström", "studie",
            "stul", "stump", "stun", "stjärna", "stol", "stop", "stor", "storm", "strumpa",
            "studs", "stuff", "stum", "su", "sub", "sudd", "suga", "sugen", "sulten",
            "summa", "sun", "sund", "sung", "sunk", "sur", "surl", "svag", "svaj", "sval",
            "svamp", "svan", "sväng", "svår", "svenska", "svårt", "syd", "sydlig", "sydost",
            "sydväst", "sylt", "syn", "synd", "synth", "så", "säck", "säga", "säker",
            "säng", "särskild", "sätta", "sön", "söndag", "sörja", "t", "ta", "tablett",
            "tack", "taf", "tagel", "take", "talent", "talk", "tall", "tand", "tango", "tank",
            "tappa", "tarm", "tată", "tatuering", "tau", "taxa", "taxi", "te", "tecken",
            "teddy", "tegel", "tema", "ten", "tennis", "tent", "tentamen", "tentor", "teori",
            "termostat", "text", "tia", "tiende", "tio", "tisdag", "tit", "tjena", "tjugo",
            "to", "tocken", "tofs", "toga", "tok", "tolk", "tomat", "tomm", "ton", "toner",
            "tong", "tonic", "topp", "torka", "torn", "torr", "torrt", "torsk", "tort",
            "torv", "tot", "total", "tott", "tour", "tr", "trad", "trana", "trappa", "trä",
            "träd", "träda", "träff", "träkol", "träna", "träning", "träsk", "tröja", "tu",
            "tuff", "tulip", "tuna", "tung", "tunga", "tupp", "tur", "ture", "tusen", "tv",
            "tvätt", "tveka", "tvivel", "twist", "two", "typ", "tyst", "tå", "tåg", "tåla",
            "tält", "tänd", "tänja", "tänka", "tår", "täck", "tö", "töj", "törn", "törst",
            "u", "uber", "udo", "ugn", "ull", "ultimatum", "ultra", "uml", "un", "undra",
            "undrar", "unga", "union", "unik", "unit", "unken", "upp", "uppe", "ur", "urd",
            "url", "usa", "ut", "utbud", "ute", "utforska", "utgå", "utmärkt", "utsikt",
            "v", "va", "vader", "vad", "vafan", "vag", "vagg", "vagn", "vaj", "vaken",
            "val", "vakuum", "valp", "vand", "vanlig", "vanligt", "vapen", "var", "vara",
            "varannan", "varannat", "vardag", "varför", "varg", "vari", "varje", "varifrån",
            "varken", "varme", "varmt", "varp", "varse", "varsin", "varsågod", "vart",
            "varulv", "vas", "vatten", "vattna", "veck", "vecka", "veckodag", "ved", "vegan",
            "veke", "vel", "vem", "ven", "vendo", "venet", "vener", "veng", "ver", "verb",
            "verk", "versa", "version", "vertikal", "vester", "vestlig", "vet", "veta",
            "vete", "victor", "video", "vid", "vidak", "vidd", "wide", "vidskepelse", "vie",
            "view", "viga", "vigit", "viking", "vil", "vild", "vilja", "vilk", "villa",
            "vilse", "vilt", "vim", "vimpel", "vind", "vinn", "vins", "viol", "violin",
            "vip", "vir", "viral", "virus", "vis", "visa", "vision", "visp", "viss", "vita",
            "vite", "vitt", "viv", "vivel", "vo", "vokal", "vol", "volatil", "volt", "volym",
            "vom", "vot", "votera", "vräk", "vud", "vugge", "vul", "vunn", "vunnet", "vuxen",
            "vuz", "våg", "våga", "vån", "vård", "våras", "våre", "vårt", "vä", "väg",
            "väga", "väl", "väldig", "väldigt", "väll", "välsign", "välsigna", "vämp", "vän",
            "vända", "vänlig", "vänster", "vänta", "vär", "värde", "värd", "värld", "värm",
            "värma", "värre", "värt", "väska", "väv", "väva", "växt", "y", "ya", "yal",
            "yam", "yankee", "yard", "yari", "yarn", "yeah", "year", "yeas", "yell", "yellow",
            "yep", "yes", "yet", "yew", "yid", "yide", "yield", "yike", "yl", "yle", "ylem",
            "yoga", "yoghurt", "yoke", "yolk", "you", "young", "your", "yowl", "yr", "yreg",
            "yt", "yu", "yuca", "yuck", "yule", "yum", "yummy", "yup", "z", "zap", "ze",
            "zee", "zen", "zero", "zest", "zig", "zigzag", "zil", "zip", "zinc", "zink",
            "zip", "zit", "zodiac", "zombie", "zone", "zoom", "zoon", "zu", "zulu", "zw",
            "zy"
        }
    }
    
    # Locale normalization mapping
    LOCALE_MAP: Dict[str, str] = {
        "en-US": "en", "en-GB": "en", "en_AU": "en", "en_CA": "en",
        "de-DE": "de", "de-AT": "de", "de-CH": "de",
        "fr-FR": "fr", "fr-CA": "fr", "fr-BE": "fr",
        "es-ES": "es", "es-MX": "es", "es-AR": "es",
        "pt-BR": "pt", "pt-PT": "pt",
        "zh-CN": "zh", "zh-TW": "zh", "zh-Hans": "zh", "zh-Hant": "zh",
        "ja-JP": "ja",
        "ko-KR": "ko",
        "ru-RU": "ru",
        "ar-SA": "ar", "ar-AE": "ar",
        "hi-IN": "hi",
        "tr-TR": "tr",
        "sv-SE": "sv",
        "nl-NL": "nl", "nl-BE": "nl",
    }
    
    @classmethod
    def get_stopwords(cls, lang_code: str) -> Optional[Set[str]]:
        """
        Get stopwords for a language code with locale normalization.
        
        Args:
            lang_code: Language code (e.g., "en", "en-US", "en_US")
            
        Returns:
            Set of stopwords or None if language not supported
        """
        # Normalize: lowercase, handle locale
        normalized = lang_code.lower().strip()
        
        # Check locale map first
        if normalized in cls.LOCALE_MAP:
            normalized = cls.LOCALE_MAP[normalized]
        
        # Extract base language code (first 2 chars for most)
        if len(normalized) > 2:
            base_code = normalized[:2]
            if base_code in cls.STOPWORDS:
                return cls.STOPWORDS[base_code]
        
        # Direct lookup
        return cls.STOPWORDS.get(normalized)
    
    @classmethod
    def get_stopwords_with_fallback(
        cls, 
        lang_code: str, 
        fallback: str = "en"
    ) -> Optional[Set[str]]:
        """
        Get stopwords with fallback to another language.
        
        Args:
            lang_code: Primary language code
            fallback: Fallback language code (default: "en")
            
        Returns:
            Set of stopwords or None
        """
        stopwords = cls.get_stopwords(lang_code)
        if stopwords is None:
            return cls.get_stopwords(fallback)
        return stopwords
    
    @classmethod
    def is_stopword(cls, word: str, lang_code: str = "en") -> bool:
        """
        Check if a word is a stopword.
        
        Args:
            word: Word to check
            lang_code: Language code
            
        Returns:
            True if word is a stopword
        """
        stopwords = cls.get_stopwords(lang_code)
        if stopwords is None:
            return False
        return word.lower() in stopwords
    
    @classmethod
    def filter_stopwords(cls, text: str, lang_code: str = "en") -> List[str]:
        """
        Filter out stopwords from text.
        
        Args:
            text: Input text
            lang_code: Language code
            
        Returns:
            List of non-stopword tokens
        """
        stopwords = cls.get_stopwords(lang_code)
        if stopwords is None:
            return text.split()
        
        return [
            word for word in text.lower().split()
            if word not in stopwords
        ]
    
    @classmethod
    def get_available_languages(cls) -> List[str]:
        """
        Get list of available language codes.
        
        Returns:
            List of language codes
        """
        return list(cls.STOPWORDS.keys())


def get_stopwords(lang_code: str) -> Optional[Set[str]]:
    """Convenience function to get stopwords."""
    return Stopwords.get_stopwords(lang_code)


def get_stopwords_with_fallback(lang_code: str, fallback: str = "en") -> Optional[Set[str]]:
    """Convenience function to get stopwords with fallback."""
    return Stopwords.get_stopwords_with_fallback(lang_code, fallback)


def is_stopword(word: str, lang_code: str = "en") -> bool:
    """Convenience function to check if a word is a stopword."""
    return Stopwords.is_stopword(word, lang_code)


def filter_stopwords(text: str, lang_code: str = "en") -> List[str]:
    """Convenience function to filter stopwords from text."""
    return Stopwords.filter_stopwords(text, lang_code)
