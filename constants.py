TARGET_RETENTION = 0.90
INITIAL_DIFFICULTY = 4.00
INITIAL_STABILITY = 1.00
PRIORITY_INTERVAL = 0.05

MIN_USERNAME_LENGTH = 4
MAX_USERNAME_LENGTH = 32
MIN_PASSWORD_LENGTH = 8

MIN_DIFFICULTY = 0
MAX_DIFFICULTY = 10

DEFAULT_LEVEL = 1

DEFAULT_DATABASE_LOCATION = "./data/ProgramDatabase.db"

PREDEFINED_SUBJECTS = ["Biology",
                        "Business",
                        "Chemistry",
                        "Computer Science",
                        "Further Maths",
                        "Geography",
                        "Health and Social Care",
                        "History",
                        "Mathematics",
                        "Media",
                        "Physics",
                        "Politics",
                        "Psychology"]

PREDEFINED_BOARDS = ["AQA",
                     "Edexcel",
                     "OCR",
                     "Pearson BTEC"]

PREDEFINED_DECKS = {
    # --- BIOLOGY ---
    "Biology : AQA": ["1 Biological molecules", "2 Cells", "3 Organisms exchange substances with their environment", "4 Genetic information, variation and relationships between organisms", "5 Energy transfers in and between organisms", "6 Organisms respond to changes in their internal and external environments", "7 Genetics, populations, evolution and ecosystems", "8 The control of gene expression"],
    "Biology : Edexcel": ["Theme 1: Evolution, Ecology and Conservation", "Theme 2: Cells, Development, Biodiversity and Conservation", "Theme 3: Energy, Exercise and Coordination", "Theme 4: Genomes, Mutations and Gene Expression"],
    "Biology : OCR": ["Module 1: Development of practical skills in biology", "Module 2: Foundations in biology", "Module 3: Exchange and transport", "Module 4: Biodiversity, evolution and disease", "Module 5: Communication, homeostasis and energy", "Module 6: Genetics, evolution and ecosystems"],

    # --- BUSINESS ---
    "Business : AQA": ["1 What is business?", "2 Managers, leadership and decision making", "3 Decision making to improve marketing performance", "4 Decision making to improve operational performance", "5 Decision making to improve financial performance", "6 Decision making to improve human resource performance", "7 Analysing the strategic position of a business", "8 Choosing strategic direction", "9 Strategic methods: how to pursue strategies", "10 Managing strategic change"],
    "Business : Edexcel": ["Theme 1: Marketing and people", "Theme 2: Managing business activities", "Theme 3: Business decisions and strategy", "Theme 4: Global business"],
    "Business : OCR": ["1 Business objectives and strategic decisions", "2 External influences", "3 Marketing", "4 Operations management", "5 Finance", "6 Human resources"],

    # --- CHEMISTRY ---
    "Chemistry : AQA": ["1 Physical chemistry", "2 Inorganic chemistry", "3 Organic chemistry"],
    "Chemistry : Edexcel": ["1 Atomic Structure and the Periodic Table", "2 Bonding and Structure", "3 Redox I", "4 Inorganic Chemistry and the Periodic Table", "5 Formulae, Equations and Amounts of Substance", "6 Organic Chemistry I", "7 Modern Analytical Techniques I", "8 Energetics I", "9 Kinetics I", "10 Equilibrium I"],
    "Chemistry : OCR": ["Module 1: Development of practical skills in chemistry", "Module 2: Foundations in chemistry", "Module 3: Periodic table and energy", "Module 4: Core organic chemistry", "Module 5: Physical chemistry and transition elements", "Module 6: Organic chemistry and analysis"],

    # --- COMPUTER SCIENCE ---
    "Computer Science : OCR": ["1.1 Characteristics of Contemporary Processor", "1.2 Software and Software Development", "1.3 Exchanging Data", "1.4 Data Types, Data Structures and Algorithms", "1.5 Legal, Moral, Cultural and Ethical Issues", "2.1 Elements of Computational Thinking", "2.2 Problem Solving and Programming", "2.3 Algorithms"],
    "Computer Science : AQA": ["1 Fundamentals of programming", "2 Fundamentals of data structures", "3 Fundamentals of algorithms", "4 Theory of computation", "5 Fundamentals of data representation", "6 Fundamentals of computer systems", "7 Fundamentals of computer organisation and architecture", "8 Consequences of uses of computing", "9 Fundamentals of communication and networking", "10 Fundamentals of databases", "11 Big Data", "12 Fundamentals of functional programming"],

    # --- MATHEMATICS ---
    "Mathematics : Edexcel": ["1 Proof", "2 Algebra and functions", "3 Coordinate geometry in the (x, y) plane", "4 Sequences and series", "5 Trigonometry", "6 Exponentials and logarithms", "7 Differentiation", "8 Integration", "9 Numerical methods", "10 Vectors", "11 Statistical sampling", "12 Data presentation and interpretation", "13 Probability", "14 Statistical distributions", "15 Statistical hypothesis testing", "16 Quantities and units in mechanics", "17 Kinematics", "18 Forces and Newton’s laws", "19 Moments"],
    "Mathematics : AQA": ["1 Proof", "2 Algebra and functions", "3 Coordinate geometry", "4 Sequences and series", "5 Trigonometry", "6 Exponentials and logarithms", "7 Differentiation", "8 Integration", "9 Numerical methods", "10 Vectors", "11 Statistical sampling", "12 Data presentation and interpretation", "13 Probability", "14 Statistical distributions", "15 Statistical hypothesis testing", "16 Mechanics: Quantities and units", "17 Kinematics", "18 Forces and Newton’s laws", "19 Moments"],
    "Mathematics : OCR": ["1 Proof", "2 Algebra", "3 Graphs", "4 Coordinate Geometry", "5 Sequences and Series", "6 Trigonometry", "7 Logarithms and Exponentials", "8 Differentiation", "9 Integration", "10 Numerical Methods", "11 Statistics: Data Presentation and Interpretation", "12 Probability", "13 Statistical Distributions", "14 Hypothesis Testing", "15 Mechanics: Quantities and units", "16 Kinematics", "17 Forces and Newton’s laws"],

    # --- FURTHER MATHS ---
    "Further Maths : Edexcel": ["1 Proof", "2 Complex numbers", "3 Matrices", "4 Further algebra and functions", "5 Further calculus", "6 Further vectors", "7 Polar coordinates", "8 Hyperbolic functions", "9 Differential equations"],
    "Further Maths : AQA": ["1 Proof", "2 Complex numbers", "3 Matrices", "4 Further Algebra and Functions", "5 Further Calculus", "6 Further Vectors", "7 Polar coordinates", "8 Hyperbolic functions", "9 Differential equations", "10 Trigonometry", "11 Numerical methods"],

    # --- GEOGRAPHY ---
    "Geography : AQA": ["1 Water and carbon cycles", "2 Hot desert systems and landscapes", "3 Coastal systems and landscapes", "4 Glacial systems and landscapes", "5 Hazards", "6 Contemporary urban environments", "7 Global systems and global governance", "8 Changing places"],
    "Geography : Edexcel": ["Area of study 1: Dynamic Landscapes", "Area of study 2: Dynamic Places", "Area of study 3: Physical Systems and Sustainability", "Area of study 4: Human Systems and Geopolitics"],

    # --- PHYSICS ---
    "Physics : AQA": ["1 Measurements and Their Errors", "2 Particles and Radiation", "3 Waves", "4 Mechanics and Materials", "5 Electricity", "6.1 Further Mechanics", "6.2 Thermal Physics", "7 Fields and Their Consequences", "8 Nuclear Physics", "9 Astrophysics", "10 Medical Physics", "11 Engineering Physics", "12 Turning points in Physics", "13 Electronics"],

    # --- PSYCHOLOGY ---
    "Psychology : AQA": ["1 Social influence", "2 Memory", "3 Attachment", "4 Psychopathology", "5 Approaches in Psychology", "6 Biopsychology", "7 Research methods", "8 Issues and debates in Psychology"],
    "Psychology : Edexcel": ["1 Social psychology", "2 Cognitive psychology", "3 Biological psychology", "4 Learning theories", "5 Clinical psychology", "6 Criminological psychology", "7 Child psychology", "8 Health psychology"],
    "Psychology : OCR": ["1 Research methods", "2 Psychological themes through core studies", "3 Applied psychology (Issues in mental health)"],

    # --- POLITICS ---
    "Politics : AQA": ["1 Government and politics of the UK", "2 Government and politics of the USA and comparative politics", "3 Political ideas (Liberalism, Conservatism, Socialism, Nationalism)"],
    "Politics : Edexcel": ["1 UK Politics", "2 UK Government", "3 Comparative Politics (USA or Global)", "4 Political Ideas"],

    # --- HISTORY ---
    "History : AQA": ["Component 1: Breadth study", "Component 2: Depth study", "Component 3: Historical investigation (NEA)"],
    "History : Edexcel": ["Paper 1: Breadth study with interpretations", "Paper 2: Depth study", "Paper 3: Themes in breadth with aspects of depth"],

    # --- MEDIA STUDIES ---
    "Media : AQA": ["1 Media Language", "2 Media Representation", "3 Media Industries", "4 Media Audiences"],
    "Media : OCR": ["1 Media Messages", "2 Evolving Media", "3 Making Media (NEA)"],

    # --- HEALTH AND SOCIAL CARE (Often BTEC/Pearson or OCR Cambridge Tech) ---
    "Health and Social Care : Pearson": ["Unit 1: Human Lifespan Development", "Unit 2: Working in Health and Social Care", "Unit 4: Enquiries into Current Research in Health and Social Care", "Unit 5: Meeting Individual Care and Support Needs"],
    "Health and Social Care : OCR": ["Unit 1: Building positive relationships in HSC", "Unit 2: Equality, diversity and rights in HSC", "Unit 3: Health, safety and security in HSC", "Unit 4: Anatomy and physiology for HSC"]
}