# =============================================================================
# University lists used to filter USPTO patent assignees
# =============================================================================

# Top Indian universities (IITs, IISc, NITs, and premier institutions)
INDIAN_UNIVERSITIES = [
    "Indian Institute of Technology Bombay",
    "Indian Institute of Technology Delhi",
    "Indian Institute of Technology Madras",
    "Indian Institute of Technology Kanpur",
    "Indian Institute of Technology Kharagpur",
    "Indian Institute of Technology Roorkee",
    "Indian Institute of Technology Guwahati",
    "Indian Institute of Technology Hyderabad",
    "Indian Institute of Technology Gandhinagar",
    "Indian Institute of Technology Jodhpur",
    "Indian Institute of Technology Bhubaneswar",
    "Indian Institute of Technology Indore",
    "Indian Institute of Technology Mandi",
    "Indian Institute of Technology Patna",
    "Indian Institute of Technology Tirupati",
    "Indian Institute of Technology Palakkad",
    "Indian Institute of Technology Dharwad",
    "Indian Institute of Technology Bhilai",
    "Indian Institute of Science",
    "Indian Institute of Science Education and Research Pune",
    "Indian Institute of Science Education and Research Kolkata",
    "Indian Institute of Science Education and Research Mohali",
    "Indian Institute of Science Education and Research Bhopal",
    "Indian Institute of Science Education and Research Thiruvananthapuram",
    "Jawaharlal Nehru University",
    "University of Delhi",
    "Tata Institute of Fundamental Research",
    "Banaras Hindu University",
    "Aligarh Muslim University",
    "Jadavpur University",
    "Anna University",
    "Manipal Academy of Higher Education",
    "Vellore Institute of Technology",
    "Amrita Vishwa Vidyapeetham",
    "SRM Institute of Science and Technology",
    "National Institute of Technology Trichy",
    "National Institute of Technology Surathkal",
    "National Institute of Technology Warangal",
    "National Institute of Technology Calicut",
    "National Institute of Technology Rourkela",
    "BITS Pilani",
]

# =============================================================================
# 200 globally recognized research universities — diverse regional coverage
# Not duplicating the Indian universities listed above
# =============================================================================
QS_UNIVERSITIES = [

    # --- United States ---
    "Massachusetts Institute of Technology",
    "Harvard University",
    "Stanford University",
    "California Institute of Technology",
    "University of Pennsylvania",
    "Cornell University",
    "University of Michigan",
    "Columbia University",
    "New York University",
    "Yale University",
    "Princeton University",
    "Johns Hopkins University",
    "University of California Los Angeles",
    "University of California San Diego",
    "University of California Davis",
    "University of California Santa Barbara",
    "Georgia Institute of Technology",
    "Rice University",
    "Duke University",
    "University of Texas at Austin",
    "University of Washington",
    "Ohio State University",
    "Pennsylvania State University",
    "University of Wisconsin-Madison",
    "Carnegie Mellon University",
    "University of Minnesota",
    "Vanderbilt University",
    "Boston University",
    "University of North Carolina at Chapel Hill",
    "Purdue University",
    "Rutgers University",
    "Indiana University",
    "University of Illinois Urbana-Champaign",

    # --- United Kingdom ---
    "Imperial College London",
    "University of Oxford",
    "University of Cambridge",
    "University College London",
    "The University of Edinburgh",
    "The University of Manchester",
    "King's College London",
    "University of Warwick",
    "University of Bristol",
    "University of Glasgow",
    "University of Birmingham",
    "Durham University",
    "University of Sheffield",
    "University of Exeter",
    "University of Leeds",
    "University of Southampton",
    "University of Nottingham",
    "Newcastle University",
    "University of St Andrews",
    "Cardiff University",
    "Queen's University Belfast",
    "University of Bath",

    # --- Australia ---
    "University of Melbourne",
    "The University of New South Wales",
    "Australian National University",
    "The University of Sydney",
    "The University of Queensland",
    "Monash University",
    "The University of Adelaide",
    "University of Western Australia",
    "Macquarie University",
    "University of Technology Sydney",
    "Curtin University",
    "RMIT University",
    "Deakin University",
    "Griffith University",
    "La Trobe University",

    # --- Canada ---
    "University of Toronto",
    "McGill University",
    "University of British Columbia",
    "McMaster University",
    "University of Alberta",
    "University of Waterloo",
    "Queen's University",
    "University of Ottawa",
    "Dalhousie University",
    "University of Calgary",

    # --- Singapore ---
    "National University of Singapore",
    "Nanyang Technological University",

    # --- Hong Kong ---
    "The University of Hong Kong",
    "The Chinese University of Hong Kong",
    "The Hong Kong University of Science and Technology",
    "City University of Hong Kong",
    "Hong Kong Polytechnic University",

    # --- China ---
    "Peking University",
    "Tsinghua University",
    "Zhejiang University",
    "Shanghai Jiao Tong University",
    "Fudan University",
    "Wuhan University",
    "Harbin Institute of Technology",
    "Nanjing University",
    "Sun Yat-sen University",
    "University of Science and Technology of China",
    "Tongji University",
    "Xi'an Jiaotong University",
    "Huazhong University of Science and Technology",
    "Shandong University",
    "Central South University",
    "Nankai University",

    # --- Japan ---
    "University of Tokyo",
    "Kyoto University",
    "Osaka University",
    "Tohoku University",
    "Tokyo Institute of Technology",
    "Nagoya University",
    "Kyushu University",
    "Hokkaido University",
    "Keio University",
    "Waseda University",
    "Kobe University",
    "Hiroshima University",
    "Tsukuba University",

    # --- South Korea ---
    "KAIST - Korea Advanced Institute of Science and Technology",
    "Seoul National University",
    "Pohang University of Science and Technology",
    "Korea University",
    "Yonsei University",
    "Sungkyunkwan University",
    "Hanyang University",

    # --- Taiwan ---
    "National Taiwan University",
    "National Tsing Hua University",
    "National Cheng Kung University",

    # --- Germany ---
    "Technical University of Munich",
    "Ludwig Maximilian University of Munich",
    "Heidelberg University",
    "RWTH Aachen University",
    "Karlsruhe Institute of Technology",
    "Free University of Berlin",
    "Humboldt University of Berlin",
    "University of Hamburg",
    "University of Göttingen",
    "University of Frankfurt",
    "University of Münster",
    "Technical University of Berlin",

    # --- Switzerland ---
    "ETH Zurich",
    "EPFL - Swiss Federal Institute of Technology Lausanne",
    "University of Zurich",
    "University of Geneva",
    "University of Basel",
    "University of Bern",

    # --- Netherlands ---
    "Delft University of Technology",
    "University of Amsterdam",
    "Leiden University",
    "Utrecht University",
    "University of Groningen",
    "Radboud University",
    "Vrije Universiteit Amsterdam",
    "Eindhoven University of Technology",

    # --- France ---
    "Sorbonne University",
    "Paris-Saclay University",
    "PSL University",
    "Ecole Polytechnique",
    "University of Bordeaux",
    "University of Strasbourg",
    "University of Lyon",

    # --- Sweden ---
    "Lund University",
    "Uppsala University",
    "KTH Royal Institute of Technology",
    "Stockholm University",
    "Chalmers University of Technology",
    "University of Gothenburg",

    # --- Belgium ---
    "KU Leuven",
    "Ghent University",
    "Vrije Universiteit Brussel",

    # --- Denmark ---
    "University of Copenhagen",
    "Aarhus University",
    "Technical University of Denmark",

    # --- Norway ---
    "Norwegian University of Science and Technology",
    "University of Oslo",

    # --- Finland ---
    "Aalto University",
    "University of Helsinki",

    # --- Austria ---
    "University of Vienna",
    "Vienna University of Technology",

    # --- Italy ---
    "Politecnico di Milano",
    "Sapienza University of Rome",
    "University of Bologna",
    "University of Padova",
    "Politecnico di Torino",

    # --- Spain ---
    "Universidad Autónoma de Madrid",
    "University of Barcelona",
    "Complutense University of Madrid",
    "Pompeu Fabra University",

    # --- Ireland ---
    "Trinity College Dublin",
    "University College Dublin",

    # --- New Zealand ---
    "University of Auckland",

    # --- Israel ---
    "Hebrew University of Jerusalem",
    "Technion - Israel Institute of Technology",
    "Tel Aviv University",

    # --- Malaysia ---
    "Universiti Malaya",
    "Universiti Putra Malaysia",
    "Universiti Sains Malaysia",

    # --- Brazil ---
    "University of São Paulo",
    "Universidade Estadual de Campinas",
    "Universidade Federal do Rio de Janeiro",

    # --- Chile ---
    "Universidad de Chile",
    "Pontificia Universidad Católica de Chile",

    # --- South Africa ---
    "University of Cape Town",
    "University of the Witwatersrand",
    "Stellenbosch University",

    # --- Russia ---
    "Lomonosov Moscow State University",
    "Saint Petersburg State University",

    # --- Saudi Arabia ---
    "King Abdullah University of Science and Technology",
    "King Fahd University of Petroleum and Minerals",

    # --- Mexico ---
    "Universidad Nacional Autónoma de México",
    "Tecnológico de Monterrey",
]

# Combined list for use in scraper queries
ALL_UNIVERSITIES = INDIAN_UNIVERSITIES + QS_UNIVERSITIES
