import frappe
from frappe.model.document import Document

APTITUDE_TEST_GROUPS = [
	{"title": "Quantitative Aptitude", "description": "Quantitative Aptitude and Numerical Ability"},
	{"title": "Logical Reasoning", "description": "Logical Reasoning and Deductive Logic"},
	{"title": "Verbal Ability", "description": "Verbal Ability and Reading Comprehension"},
	{"title": "General Knowledge", "description": "General Knowledge and Awareness"},
	{"title": "Current Affairs", "description": "Current Affairs"},
	{"title": "Data Interpretation", "description": "Data Interpretation and Analysis"},
	{"title": "General English", "description": "General English Language Skills"},
]

HIGHER_SECONDARY_ENTRANCE_PROGRAMS = [
	{
		"title": "JEE Entrance",
		"description": "Joint Entrance Examination preparation for engineering admissions.",
		"courses": [
			{
				"title": "JEE Physics Class 11",
				"description": "Class 11 Physics syllabus units for JEE Entrance.",
				"source": "NTA JEE Main 2026 Syllabus",
				"chapters": [
					{
						"title": "Physics and Measurement",
						"lessons": [
							"Units of Measurement",
							"Errors in Measurement",
							"Dimensions of Physical Quantities",
						],
					},
					{
						"title": "Kinematics",
						"lessons": [
							"Motion in a Straight Line",
							"Motion in a Plane",
							"Projectile Motion",
							"Uniform Circular Motion",
						],
					},
					{
						"title": "Laws of Motion",
						"lessons": [
							"Newton's Laws of Motion",
							"Friction",
							"Circular Motion Dynamics",
						],
					},
					{
						"title": "Work, Energy, and Power",
						"lessons": [
							"Work Done by Constant and Variable Forces",
							"Kinetic and Potential Energy",
							"Conservation of Mechanical Energy",
							"Power",
						],
					},
					{
						"title": "Rotational Motion",
						"lessons": [
							"Centre of Mass",
							"Torque and Angular Momentum",
							"Moment of Inertia",
							"Equilibrium of Rigid Bodies",
						],
					},
					{
						"title": "Gravitation",
						"lessons": [
							"Universal Law of Gravitation",
							"Acceleration Due to Gravity",
							"Gravitational Potential Energy",
							"Satellites",
						],
					},
					{
						"title": "Properties of Solids and Liquids",
						"lessons": [
							"Elastic Behaviour",
							"Pressure in Fluids",
							"Viscosity",
							"Surface Tension",
						],
					},
					{
						"title": "Thermodynamics",
						"lessons": [
							"Thermal Equilibrium",
							"First Law of Thermodynamics",
							"Heat Engines",
							"Second Law of Thermodynamics",
						],
					},
					{
						"title": "Kinetic Theory of Gases",
						"lessons": [
							"Ideal Gas Equation",
							"Kinetic Interpretation of Temperature",
							"Degrees of Freedom",
							"Mean Free Path",
						],
					},
					{
						"title": "Oscillations and Waves",
						"lessons": [
							"Simple Harmonic Motion",
							"Energy in SHM",
							"Wave Motion",
							"Sound Waves",
						],
					},
				],
			},
			{
				"title": "JEE Physics Class 12",
				"description": "Class 12 Physics syllabus units for JEE Entrance.",
				"source": "NTA JEE Main 2026 Syllabus",
				"chapters": [
					{
						"title": "Electrostatics",
						"lessons": [
							"Electric Charge and Coulomb's Law",
							"Electric Field and Potential",
							"Gauss Law",
							"Capacitance",
						],
					},
					{
						"title": "Current Electricity",
						"lessons": [
							"Electric Current and Drift Velocity",
							"Ohm's Law",
							"Kirchhoff's Laws",
							"Electrical Instruments",
						],
					},
					{
						"title": "Magnetic Effects of Current and Magnetism",
						"lessons": [
							"Biot-Savart Law",
							"Ampere's Law",
							"Force on Moving Charges",
							"Magnetic Properties of Materials",
						],
					},
					{
						"title": "Electromagnetic Induction and Alternating Currents",
						"lessons": [
							"Faraday's Law",
							"Lenz's Law",
							"AC Circuits",
							"Transformers",
						],
					},
					{
						"title": "Electromagnetic Waves",
						"lessons": [
							"Displacement Current",
							"Electromagnetic Spectrum",
							"Applications of EM Waves",
						],
					},
					{
						"title": "Optics",
						"lessons": [
							"Reflection and Refraction",
							"Lens and Mirror Formulae",
							"Interference and Diffraction",
							"Polarisation",
						],
					},
					{
						"title": "Dual Nature of Matter and Radiation",
						"lessons": [
							"Photoelectric Effect",
							"de Broglie Wavelength",
							"Matter Waves",
						],
					},
					{
						"title": "Atoms and Nuclei",
						"lessons": [
							"Bohr Model",
							"Atomic Spectra",
							"Nuclear Composition",
							"Radioactivity",
						],
					},
					{
						"title": "Electronic Devices",
						"lessons": [
							"Semiconductors",
							"Diodes",
							"Transistors",
							"Logic Gates",
						],
					},
				],
			},
			{
				"title": "JEE Chemistry Class 11",
				"description": "Class 11 Chemistry syllabus units for JEE Entrance.",
				"source": "NTA JEE Main 2026 Syllabus",
				"chapters": [
					{
						"title": "Some Basic Concepts in Chemistry",
						"lessons": [
							"Mole Concept",
							"Stoichiometry",
							"Concentration Terms",
							"Limiting Reagent",
						],
					},
					{
						"title": "Atomic Structure",
						"lessons": [
							"Bohr Model",
							"Quantum Numbers",
							"Electronic Configuration",
							"de Broglie Relation",
						],
					},
					{
						"title": "Chemical Bonding and Molecular Structure",
						"lessons": [
							"Ionic and Covalent Bonding",
							"VSEPR Theory",
							"Hybridisation",
							"Molecular Orbital Theory",
						],
					},
					{
						"title": "Chemical Thermodynamics",
						"lessons": [
							"First Law of Thermodynamics",
							"Enthalpy",
							"Entropy",
							"Gibbs Free Energy",
						],
					},
					{
						"title": "Solutions and Equilibrium",
						"lessons": [
							"Solubility and Concentration",
							"Chemical Equilibrium",
							"Ionic Equilibrium",
							"pH and Buffer Solutions",
						],
					},
					{
						"title": "Redox Reactions and Electrochemistry Basics",
						"lessons": [
							"Oxidation and Reduction",
							"Balancing Redox Reactions",
							"Electrode Potential",
						],
					},
					{
						"title": "Classification of Elements and Periodicity",
						"lessons": [
							"Modern Periodic Law",
							"Periodic Trends",
							"Effective Nuclear Charge",
						],
					},
					{
						"title": "Organic Chemistry Basics",
						"lessons": [
							"Nomenclature",
							"Isomerism",
							"Electronic Effects",
							"Reaction Intermediates",
						],
					},
					{
						"title": "Hydrocarbons",
						"lessons": [
							"Alkanes",
							"Alkenes",
							"Alkynes",
							"Aromatic Hydrocarbons",
						],
					},
				],
			},
			{
				"title": "JEE Chemistry Class 12",
				"description": "Class 12 Chemistry syllabus units for JEE Entrance.",
				"source": "NTA JEE Main 2026 Syllabus",
				"chapters": [
					{
						"title": "Chemical Kinetics",
						"lessons": [
							"Rate of Reaction",
							"Order and Molecularity",
							"Integrated Rate Equations",
							"Activation Energy",
						],
					},
					{
						"title": "Electrochemistry",
						"lessons": [
							"Galvanic Cells",
							"Nernst Equation",
							"Conductance",
							"Electrolysis",
						],
					},
					{
						"title": "p-Block Elements",
						"lessons": [
							"Group 13 and 14 Elements",
							"Group 15 Elements",
							"Group 16 Elements",
							"Group 17 and 18 Elements",
						],
					},
					{
						"title": "d- and f-Block Elements",
						"lessons": [
							"Transition Elements",
							"Lanthanoids",
							"Actinoids",
							"Magnetic Properties",
						],
					},
					{
						"title": "Coordination Compounds",
						"lessons": [
							"Nomenclature",
							"Isomerism",
							"Bonding in Coordination Compounds",
							"Stability and Applications",
						],
					},
					{
						"title": "Haloalkanes and Haloarenes",
						"lessons": [
							"Nucleophilic Substitution",
							"Elimination Reactions",
							"Aryl Halides",
						],
					},
					{
						"title": "Alcohols, Phenols, and Ethers",
						"lessons": [
							"Preparation and Properties of Alcohols",
							"Phenols",
							"Ethers",
						],
					},
					{
						"title": "Aldehydes, Ketones, and Carboxylic Acids",
						"lessons": [
							"Nucleophilic Addition",
							"Oxidation and Reduction",
							"Carboxylic Acid Derivatives",
						],
					},
					{
						"title": "Amines and Biomolecules",
						"lessons": [
							"Amines",
							"Carbohydrates",
							"Proteins",
							"Nucleic Acids",
						],
					},
				],
			},
			{
				"title": "JEE Mathematics Class 11",
				"description": "Class 11 Mathematics syllabus units for JEE Entrance.",
				"source": "NTA JEE Main 2026 Syllabus",
				"chapters": [
					{
						"title": "Sets, Relations, and Functions",
						"lessons": [
							"Sets and Operations",
							"Relations",
							"Functions",
							"Composition of Functions",
						],
					},
					{
						"title": "Complex Numbers and Quadratic Equations",
						"lessons": [
							"Complex Number Algebra",
							"Argand Plane",
							"Quadratic Equations",
							"Nature of Roots",
						],
					},
					{
						"title": "Matrices and Determinants",
						"lessons": [
							"Matrix Operations",
							"Determinants",
							"Inverse of a Matrix",
							"Linear Equations",
						],
					},
					{
						"title": "Permutations and Combinations",
						"lessons": [
							"Fundamental Principle of Counting",
							"Permutations",
							"Combinations",
						],
					},
					{
						"title": "Binomial Theorem",
						"lessons": [
							"Binomial Expansion",
							"General Term",
							"Middle Term",
						],
					},
					{
						"title": "Sequence and Series",
						"lessons": [
							"Arithmetic Progression",
							"Geometric Progression",
							"Special Series",
						],
					},
					{
						"title": "Coordinate Geometry",
						"lessons": [
							"Straight Lines",
							"Circle",
							"Parabola",
							"Ellipse and Hyperbola",
						],
					},
					{
						"title": "Three Dimensional Geometry",
						"lessons": [
							"Coordinates in Space",
							"Direction Cosines",
							"Distance Formula",
						],
					},
					{
						"title": "Statistics and Probability",
						"lessons": [
							"Measures of Dispersion",
							"Probability Basics",
							"Conditional Probability",
							"Bayes Theorem",
						],
					},
				],
			},
			{
				"title": "JEE Mathematics Class 12",
				"description": "Class 12 Mathematics syllabus units for JEE Entrance.",
				"source": "NTA JEE Main 2026 Syllabus",
				"chapters": [
					{
						"title": "Trigonometry",
						"lessons": [
							"Trigonometric Identities",
							"Inverse Trigonometric Functions",
							"Heights and Distances",
						],
					},
					{
						"title": "Limit, Continuity, and Differentiability",
						"lessons": [
							"Limits",
							"Continuity",
							"Differentiability",
							"Derivative Rules",
						],
					},
					{
						"title": "Integral Calculus",
						"lessons": [
							"Indefinite Integration",
							"Definite Integration",
							"Area Under Curves",
						],
					},
					{
						"title": "Differential Equations",
						"lessons": [
							"Order and Degree",
							"Formation of Differential Equations",
							"Solution of First Order Equations",
						],
					},
					{
						"title": "Vector Algebra",
						"lessons": [
							"Vector Operations",
							"Scalar Product",
							"Vector Product",
						],
					},
					{
						"title": "Mathematical Reasoning",
						"lessons": [
							"Statements",
							"Logical Connectives",
							"Implications",
						],
					},
				],
			},
		],
	},
	{
		"title": "NEET Entrance",
		"description": "National Eligibility cum Entrance Test preparation for medical admissions.",
		"courses": [
			{
				"title": "NEET Physics Class 11",
				"description": "Class 11 Physics syllabus units for NEET Entrance.",
				"source": "NTA NEET UG 2026 Syllabus",
				"chapters": [
					{"title": "Physics and Measurement", "lessons": ["Units and Dimensions", "Errors in Measurement", "Significant Figures"]},
					{"title": "Kinematics", "lessons": ["Motion in a Straight Line", "Motion in a Plane", "Projectile Motion", "Relative Velocity"]},
					{"title": "Laws of Motion", "lessons": ["Newton's Laws", "Friction", "Equilibrium of Forces", "Circular Motion"]},
					{"title": "Work, Energy, and Power", "lessons": ["Work-Energy Theorem", "Conservative Forces", "Power", "Collisions"]},
					{"title": "Rotational Motion", "lessons": ["Centre of Mass", "Torque", "Moment of Inertia", "Angular Momentum"]},
					{"title": "Gravitation", "lessons": ["Universal Gravitation", "Gravitational Field", "Escape Velocity", "Satellites"]},
					{"title": "Properties of Solids and Liquids", "lessons": ["Elasticity", "Fluid Pressure", "Viscosity", "Surface Tension"]},
					{"title": "Thermodynamics", "lessons": ["Thermal Equilibrium", "First Law", "Second Law", "Heat Engines"]},
					{"title": "Kinetic Theory of Gases", "lessons": ["Ideal Gas Equation", "Kinetic Energy of Gas Molecules", "Degrees of Freedom"]},
					{"title": "Oscillations and Waves", "lessons": ["Simple Harmonic Motion", "Wave Motion", "Sound Waves", "Doppler Effect"]},
				],
			},
			{
				"title": "NEET Physics Class 12",
				"description": "Class 12 Physics syllabus units for NEET Entrance.",
				"source": "NTA NEET UG 2026 Syllabus",
				"chapters": [
					{"title": "Electrostatics", "lessons": ["Electric Charges", "Electric Field", "Electric Potential", "Capacitors"]},
					{"title": "Current Electricity", "lessons": ["Ohm's Law", "Resistivity", "Kirchhoff's Laws", "Potentiometer"]},
					{"title": "Magnetic Effects of Current and Magnetism", "lessons": ["Magnetic Field", "Moving Coil Galvanometer", "Torque on a Current Loop", "Magnetism"]},
					{"title": "Electromagnetic Induction and Alternating Currents", "lessons": ["Faraday's Law", "Self and Mutual Inductance", "AC Circuits", "Transformer"]},
					{"title": "Electromagnetic Waves", "lessons": ["Electromagnetic Spectrum", "Properties of EM Waves", "Applications"]},
					{"title": "Optics", "lessons": ["Ray Optics", "Optical Instruments", "Wave Optics", "Polarisation"]},
					{"title": "Dual Nature of Matter and Radiation", "lessons": ["Photoelectric Effect", "Matter Waves", "de Broglie Hypothesis"]},
					{"title": "Atoms and Nuclei", "lessons": ["Atomic Models", "Nuclear Properties", "Radioactivity", "Nuclear Energy"]},
					{"title": "Electronic Devices", "lessons": ["Semiconductor Diode", "Transistor", "Logic Gates", "Communication Systems"]},
				],
			},
			{
				"title": "NEET Chemistry Class 11",
				"description": "Class 11 Chemistry syllabus units for NEET Entrance.",
				"source": "NTA NEET UG 2026 Syllabus",
				"chapters": [
					{"title": "Some Basic Concepts in Chemistry", "lessons": ["Mole Concept", "Stoichiometry", "Concentration Terms", "Atomic and Molecular Mass"]},
					{"title": "Atomic Structure", "lessons": ["Bohr Model", "Quantum Numbers", "Electronic Configuration", "Atomic Spectra"]},
					{"title": "Chemical Bonding and Molecular Structure", "lessons": ["Ionic Bonding", "Covalent Bonding", "VSEPR Theory", "Hybridisation"]},
					{"title": "Chemical Thermodynamics", "lessons": ["Thermodynamic Terms", "Enthalpy", "Entropy", "Gibbs Energy"]},
					{"title": "Solutions and Equilibrium", "lessons": ["Chemical Equilibrium", "Ionic Equilibrium", "pH", "Solubility Product"]},
					{"title": "Redox Reactions and Electrochemistry", "lessons": ["Oxidation Number", "Redox Balancing", "Electrochemical Cells"]},
					{"title": "Classification of Elements and Periodicity", "lessons": ["Periodic Table", "Atomic Radius", "Ionisation Enthalpy", "Electronegativity"]},
					{"title": "Organic Chemistry Basics", "lessons": ["Nomenclature", "Isomerism", "Reaction Mechanisms", "Purification Methods"]},
					{"title": "Hydrocarbons", "lessons": ["Alkanes", "Alkenes", "Alkynes", "Aromatic Hydrocarbons"]},
				],
			},
			{
				"title": "NEET Chemistry Class 12",
				"description": "Class 12 Chemistry syllabus units for NEET Entrance.",
				"source": "NTA NEET UG 2026 Syllabus",
				"chapters": [
					{"title": "Chemical Kinetics", "lessons": ["Rate Law", "Order of Reaction", "Half-Life", "Activation Energy"]},
					{"title": "Electrochemistry", "lessons": ["Electrochemical Cells", "Nernst Equation", "Conductance", "Electrolysis"]},
					{"title": "p-Block Elements", "lessons": ["Group 13 Elements", "Group 14 Elements", "Group 15 to 18 Elements"]},
					{"title": "d- and f-Block Elements", "lessons": ["Transition Elements", "Lanthanoids", "Actinoids", "Complex Formation"]},
					{"title": "Coordination Compounds", "lessons": ["Nomenclature", "Isomerism", "Bonding", "Applications"]},
					{"title": "Haloalkanes and Haloarenes", "lessons": ["Preparation", "Nucleophilic Substitution", "Elimination", "Aryl Halides"]},
					{"title": "Alcohols, Phenols, and Ethers", "lessons": ["Alcohols", "Phenols", "Ethers", "Named Reactions"]},
					{"title": "Aldehydes, Ketones, and Carboxylic Acids", "lessons": ["Carbonyl Compounds", "Carboxylic Acids", "Nucleophilic Addition", "Oxidation and Reduction"]},
					{"title": "Amines and Biomolecules", "lessons": ["Amines", "Carbohydrates", "Proteins", "Nucleic Acids"]},
				],
			},
			{
				"title": "NEET Biology Class 11",
				"description": "Class 11 Biology syllabus units for NEET Entrance.",
				"source": "NTA NEET UG 2026 Syllabus",
				"chapters": [
					{"title": "Diversity in Living World", "lessons": ["The Living World", "Biological Classification", "Plant Kingdom", "Animal Kingdom"]},
					{"title": "Structural Organisation in Animals and Plants", "lessons": ["Morphology of Flowering Plants", "Anatomy of Flowering Plants", "Structural Organisation in Animals"]},
					{"title": "Cell Structure and Function", "lessons": ["Cell Theory", "Cell Organelles", "Biomolecules", "Cell Cycle and Cell Division"]},
					{"title": "Plant Physiology", "lessons": ["Photosynthesis", "Respiration in Plants", "Plant Growth and Development", "Transport in Plants"]},
					{"title": "Human Physiology", "lessons": ["Digestion and Absorption", "Breathing and Exchange of Gases", "Body Fluids and Circulation", "Excretory Products and Elimination", "Neural Control and Coordination"]},
				],
			},
			{
				"title": "NEET Biology Class 12",
				"description": "Class 12 Biology syllabus units for NEET Entrance.",
				"source": "NTA NEET UG 2026 Syllabus",
				"chapters": [
					{"title": "Reproduction", "lessons": ["Reproduction in Organisms", "Sexual Reproduction in Flowering Plants", "Human Reproduction", "Reproductive Health"]},
					{"title": "Genetics and Evolution", "lessons": ["Principles of Inheritance", "Molecular Basis of Inheritance", "Evolution", "Human Health Genetics"]},
					{"title": "Biology and Human Welfare", "lessons": ["Human Health and Disease", "Microbes in Human Welfare", "Strategies for Enhancement in Food Production"]},
					{"title": "Biotechnology and Its Applications", "lessons": ["Biotechnology Principles", "Biotechnology Processes", "Medical Applications", "Agricultural Applications"]},
					{"title": "Ecology and Environment", "lessons": ["Organisms and Populations", "Ecosystem", "Biodiversity and Conservation", "Environmental Issues"]},
				],
			},
		],
	},
]

PROFESSIONAL_PROGRAMS = [
	{
		"title": "CA",
		"description": "Chartered Accountancy",
		"courses": [
			{
				"title": "CA Foundation",
				"description": "Foundation level for Chartered Accountancy.",
				"source": "ICAI Foundation Course - New Scheme of Education and Training",
				"chapters": [
					{
						"title": "Accounting",
						"lessons": [
							"Accounting Principles",
							"Accounting Standards",
							"Journal Entries",
							"Ledger Posting",
							"Trial Balance",
							"Bank Reconciliation Statement",
							"Depreciation Accounting",
							"Final Accounts",
							"Partnership Accounts",
							"Company Accounts",
						],
					},
					{
						"title": "Business Laws",
						"lessons": [
							"Indian Regulatory Framework",
							"Indian Contract Act, 1872",
							"Sale of Goods Act, 1930",
							"Indian Partnership Act, 1932",
							"Limited Liability Partnership Act, 2008",
							"Companies Act, 2013 Basics",
							"Negotiable Instruments Act, 1881",
						],
					},
					{
						"title": "Quantitative Aptitude",
						"lessons": [
							"Ratio and Proportion",
							"Equations and Linear Inequalities",
							"Time Value of Money",
							"Permutations and Combinations",
							"Sequence and Series",
							"Statistical Description of Data",
							"Measures of Central Tendency and Dispersion",
							"Probability",
						],
					},
					{
						"title": "Business Economics",
						"lessons": [
							"Nature and Scope of Business Economics",
							"Theory of Demand and Supply",
							"Theory of Production and Cost",
							"Price Determination in Different Markets",
							"Business Cycles",
							"Determination of National Income",
							"Public Finance",
							"Money Market",
							"International Trade",
							"Indian Economy",
						],
					},
				],
			},
			{
				"title": "CA Intermediate - Group 1",
				"description": "Intermediate Group 1 for Chartered Accountancy.",
				"source": "ICAI Intermediate Course - New Scheme of Education and Training",
				"chapters": [
					{
						"title": "Advanced Accounting",
						"lessons": [
							"Accounting Standards",
							"Framework for Preparation and Presentation of Financial Statements",
							"Presentation and Disclosure Based Accounting Standards",
							"Assets Based Accounting Standards",
							"Liabilities Based Accounting Standards",
							"Accounting for Branches",
							"Amalgamation of Companies",
							"Consolidated Financial Statements",
						],
					},
					{
						"title": "Corporate and Other Laws",
						"lessons": [
							"Companies Act, 2013 Preliminary",
							"Incorporation of Company",
							"Prospectus and Allotment of Securities",
							"Share Capital and Debentures",
							"Acceptance of Deposits",
							"Registration of Charges",
							"Management and Administration",
							"Declaration and Payment of Dividend",
							"Negotiable Instruments Act, 1881",
							"General Clauses Act, 1897",
							"Interpretation of Statutes",
						],
					},
					{
						"title": "Taxation",
						"lessons": [
							"Income Tax Basics",
							"Residential Status and Scope of Total Income",
							"Heads of Income",
							"Clubbing and Set Off of Losses",
							"Deductions from Gross Total Income",
							"Computation of Total Income and Tax Liability",
							"Advance Tax and TDS",
							"GST Concepts",
							"Supply Under GST",
							"Input Tax Credit",
							"Registration and Tax Invoice",
							"GST Returns and Payment of Tax",
						],
					},
				],
			},
			{
				"title": "CA Intermediate - Group 2",
				"description": "Intermediate Group 2 for Chartered Accountancy.",
				"source": "ICAI Intermediate Course - New Scheme of Education and Training",
				"chapters": [
					{
						"title": "Cost and Management Accounting",
						"lessons": [
							"Overview of Cost and Management Accounting",
							"Material Cost",
							"Employee Cost",
							"Overheads",
							"Activity Based Costing",
							"Cost Sheet",
							"Unit and Batch Costing",
							"Job and Contract Costing",
							"Process Costing",
							"Marginal Costing",
							"Budgetary Control",
							"Standard Costing",
						],
					},
					{
						"title": "Auditing and Ethics",
						"lessons": [
							"Nature, Objective and Scope of Audit",
							"Audit Strategy, Planning and Programme",
							"Risk Assessment and Internal Control",
							"Audit Evidence",
							"Audit of Items of Financial Statements",
							"Audit Documentation",
							"Completion and Review",
							"Company Audit",
							"Audit Report",
							"Professional Ethics",
						],
					},
					{
						"title": "Financial Management and Strategic Management",
						"lessons": [
							"Financial Management Scope and Objectives",
							"Types of Financing",
							"Financial Analysis and Planning",
							"Cost of Capital",
							"Financing Decisions",
							"Capital Investment and Dividend Decisions",
							"Management of Working Capital",
							"Introduction to Strategic Management",
							"Strategic Analysis",
							"Strategic Choices",
							"Strategy Implementation and Evaluation",
						],
					},
				],
			},
			{
				"title": "CA Final - Group 1",
				"description": "Final Group 1 for Chartered Accountancy.",
				"source": "ICAI Final Course - New Scheme of Education and Training",
				"chapters": [
					{
						"title": "Financial Reporting",
						"lessons": [
							"Ind AS Framework",
							"Presentation of Financial Statements",
							"Share Based Payment",
							"Business Combinations",
							"Consolidated Financial Statements",
							"Financial Instruments",
							"Revenue Recognition",
							"Leases",
							"Income Taxes",
							"Analysis of Financial Statements",
						],
					},
					{
						"title": "Advanced Financial Management",
						"lessons": [
							"Financial Policy and Corporate Strategy",
							"Risk Management",
							"Security Analysis",
							"Security Valuation",
							"Portfolio Management",
							"Securitization",
							"Mutual Funds",
							"Derivatives Analysis and Valuation",
							"Foreign Exchange Exposure and Risk Management",
							"International Financial Management",
							"Interest Rate Risk Management",
							"Business Valuation",
							"Mergers, Acquisitions and Corporate Restructuring",
							"Startup Finance",
						],
					},
					{
						"title": "Advanced Auditing, Assurance and Professional Ethics",
						"lessons": [
							"Quality Control and Engagement Standards",
							"Audit Planning, Strategy and Execution",
							"Risk Assessment and Internal Control",
							"Special Aspects of Auditing in Automated Environment",
							"Audit of Limited Companies",
							"AUDIT Reports",
							"Audit Committee and Corporate Governance",
							"Audit of Consolidated Financial Statements",
							"Due Diligence, Investigation and Forensic Audit",
							"Professional Ethics",
						],
					},
				],
			},
			{
				"title": "CA Final - Group 2",
				"description": "Final Group 2 for Chartered Accountancy.",
				"source": "ICAI Final Course - New Scheme of Education and Training",
				"chapters": [
					{
						"title": "Direct Tax Laws & International Taxation",
						"lessons": [
							"Basic Concepts and Residential Status",
							"Profits and Gains of Business or Profession",
							"Capital Gains",
							"Income from Other Sources",
							"Assessment of Various Entities",
							"Tax Planning, Tax Avoidance and Tax Evasion",
							"Deduction, Collection and Recovery of Tax",
							"Income Tax Authorities",
							"Appeals and Revision",
							"Transfer Pricing",
							"Double Taxation Relief",
							"Advance Rulings",
						],
					},
					{
						"title": "Indirect Tax Laws",
						"lessons": [
							"GST Constitutional Framework",
							"Supply Under GST",
							"Charge of GST",
							"Place of Supply",
							"Exemptions from GST",
							"Time of Supply",
							"Value of Supply",
							"Input Tax Credit",
							"Registration",
							"Tax Invoice, Credit and Debit Notes",
							"Accounts and Records",
							"Returns and Payment of Tax",
							"Refunds",
							"Customs Law Basics",
						],
					},
					{
						"title": "Integrated Business Solutions",
						"lessons": [
							"Case Study Approach",
							"Integration of Accounting and Taxation",
							"Integration of Auditing and Law",
							"Strategic Management Case Analysis",
							"Risk and Governance Case Analysis",
							"Multidisciplinary Problem Solving",
						],
					},
				],
			},
		],
	},
		{
			"title": "ACCA",
			"description": "Association of Chartered Certified Accountants",
		"courses": [
			{
				"title": "ACCA Applied Knowledge",
				"description": "Applied Knowledge level for ACCA.",
				"source": "ACCA Qualification Structure",
				"chapters": [
					{"title": "Business and Technology (BT)", "lessons": ["Business Organisation", "Governance and Ethics", "Accounting and Reporting Systems", "Internal Control", "Leading and Managing Individuals and Teams", "Personal Effectiveness", "Data and Digital Technology"]},
					{"title": "Financial Accounting (FA)", "lessons": ["Financial Reporting Principles", "Double Entry and Accounting Systems", "Recording Transactions and Events", "Preparing a Trial Balance", "Preparing Basic Financial Statements", "Interpreting Financial Statements"]},
					{"title": "Management Accounting (MA)", "lessons": ["Nature and Purpose of Management Information", "Cost Classification", "Budgeting", "Standard Costing", "Performance Measurement", "Short Term Decision Making"]},
				],
			},
			{
				"title": "ACCA Applied Skills",
				"description": "Applied Skills level for ACCA.",
				"source": "ACCA Qualification Structure",
				"chapters": [
					{"title": "Corporate and Business Law (LW)", "lessons": ["Legal System", "Contract Law", "Employment Law", "Company Formation", "Capital and Financing", "Management and Administration", "Insolvency Law"]},
					{"title": "Performance Management (PM)", "lessons": ["Information, Technologies and Systems", "Specialist Cost and Management Accounting Techniques", "Decision Making Techniques", "Budgeting and Control", "Performance Measurement and Control"]},
					{"title": "Taxation (TX)", "lessons": ["Income Tax", "Corporation Tax", "Chargeable Gains", "National Insurance Contributions", "Value Added Tax", "Tax Administration"]},
					{"title": "Financial Reporting (FR)", "lessons": ["Conceptual Framework", "Regulatory Framework", "Accounting for Transactions", "Financial Statements", "Consolidated Financial Statements", "Financial Statement Analysis"]},
					{"title": "Audit and Assurance (AA)", "lessons": ["Audit Framework and Regulation", "Planning and Risk Assessment", "Internal Control", "Audit Evidence", "Review and Reporting"]},
					{"title": "Financial Management (FM)", "lessons": ["Financial Management Function", "Working Capital Management", "Investment Appraisal", "Business Finance", "Cost of Capital", "Business Valuations", "Risk Management"]},
				],
			},
			{
				"title": "ACCA Strategic Professional",
				"description": "Strategic Professional level for ACCA.",
				"source": "ACCA Qualification Structure",
				"chapters": [
					{"title": "Strategic Business Leader (SBL)", "lessons": ["Leadership", "Governance", "Strategy", "Risk", "Technology and Data Analytics", "Organisational Control", "Finance in Planning and Decision Making", "Innovation and Change Management"]},
					{"title": "Strategic Business Reporting (SBR)", "lessons": ["Ethical and Professional Principles", "Financial Reporting Framework", "Reporting Financial Performance", "Financial Statements of Groups", "Current Issues in Financial Reporting"]},
					{"title": "Advanced Financial Management (AFM)", "lessons": ["Role of Senior Financial Adviser", "Advanced Investment Appraisal", "Acquisitions and Mergers", "Corporate Reconstruction", "Treasury and Advanced Risk Management"]},
					{"title": "Advanced Performance Management (APM)", "lessons": ["Strategic Planning and Control", "Economic and Regulatory Environment", "Performance Measurement Systems", "Strategic Performance Measurement", "Performance Evaluation"]},
					{"title": "Advanced Taxation (ATX)", "lessons": ["Tax Systems and Ethics", "Income and Corporate Taxes", "Chargeable Gains", "Inheritance Tax", "International Tax Issues", "Tax Planning"]},
					{"title": "Advanced Audit and Assurance (AAA)", "lessons": ["Regulatory Environment", "Professional and Ethical Considerations", "Quality Management", "Planning and Conducting an Audit", "Completion and Reporting"]},
				],
				},
			],
		},
	{
		"title": "CMA India",
		"description": "Cost and Management Accountant India",
		"courses": [
			{
				"title": "CMA India Foundation",
				"description": "Foundation level for CMA India.",
				"source": "ICMAI Syllabus 2022 Foundation Course Curriculum",
				"chapters": [
					{"title": "Fundamentals of Business Laws and Business Communication", "lessons": ["Indian Contracts", "Sale of Goods", "Negotiable Instruments", "Business Communication", "Business Correspondence"]},
					{"title": "Fundamentals of Financial and Cost Accounting", "lessons": ["Accounting Basics", "Journal and Ledger", "Trial Balance", "Depreciation", "Final Accounts", "Cost Accounting Fundamentals"]},
					{"title": "Fundamentals of Business Mathematics and Statistics", "lessons": ["Arithmetic", "Algebra", "Calculus Basics", "Statistical Representation", "Measures of Central Tendency", "Probability"]},
					{"title": "Fundamentals of Business Economics and Management", "lessons": ["Micro Economics", "Theory of Demand and Supply", "Production and Cost", "Market Forms", "Business Environment", "Management Process"]},
				],
			},
			{
				"title": "CMA India Intermediate - Group 1",
				"description": "Intermediate Group 1 for CMA India.",
				"source": "ICMAI Syllabus 2022 Intermediate Course Curriculum",
				"chapters": [
					{"title": "Business Laws and Ethics", "lessons": ["Commercial Laws", "Industrial Laws", "Corporate Laws", "Ethics and Business", "Corporate Governance"]},
					{"title": "Financial Accounting", "lessons": ["Accounting Standards", "Partnership Accounts", "Branch and Departmental Accounts", "Hire Purchase", "Company Accounts", "Accounting for Banking and Insurance"]},
					{"title": "Direct and Indirect Taxation", "lessons": ["Income Tax Basics", "Heads of Income", "Deductions", "Assessment Procedure", "GST Concepts", "Input Tax Credit", "Customs Basics"]},
					{"title": "Cost Accounting", "lessons": ["Material Cost", "Employee Cost", "Overheads", "Cost Bookkeeping", "Methods of Costing", "Cost Accounting Techniques"]},
				],
			},
			{
				"title": "CMA India Intermediate - Group 2",
				"description": "Intermediate Group 2 for CMA India.",
				"source": "ICMAI Syllabus 2022 Intermediate Course Curriculum",
				"chapters": [
					{"title": "Operations Management and Strategic Management", "lessons": ["Operations Planning", "Production Planning", "Productivity Management", "Quality Management", "Strategic Analysis", "Strategy Formulation"]},
					{"title": "Corporate Accounting and Auditing", "lessons": ["Company Accounts", "Consolidated Accounts", "Corporate Restructuring", "Audit Planning", "Internal Control", "Company Audit"]},
					{"title": "Financial Management and Business Data Analytics", "lessons": ["Financial Management Objectives", "Working Capital Management", "Capital Budgeting", "Cost of Capital", "Data Analytics Basics", "Data Visualization"]},
					{"title": "Management Accounting", "lessons": ["Budgetary Control", "Standard Costing", "Marginal Costing", "Decision Making", "Performance Measurement", "Responsibility Accounting"]},
				],
			},
			{
				"title": "CMA India Final - Group 3",
				"description": "Final Group 3 for CMA India.",
				"source": "ICMAI Syllabus 2022 Final Course Curriculum",
				"chapters": [
					{"title": "Corporate and Economic Laws", "lessons": ["Companies Act", "Securities Laws", "Economic Laws", "Competition Law", "Insolvency and Bankruptcy"]},
					{"title": "Strategic Financial Management", "lessons": ["Investment Decisions", "Portfolio Management", "Derivatives", "Foreign Exchange Risk", "Corporate Valuation", "Mergers and Acquisitions"]},
					{"title": "Direct Tax Laws and International Taxation", "lessons": ["Assessment of Companies", "Tax Planning", "Transfer Pricing", "International Taxation", "Tax Treaties", "Appeals and Revision"]},
					{"title": "Strategic Cost Management", "lessons": ["Cost Management Techniques", "Activity Based Management", "Target Costing", "Life Cycle Costing", "Throughput Accounting", "Performance Management"]},
				],
			},
			{
				"title": "CMA India Final - Group 4",
				"description": "Final Group 4 for CMA India.",
				"source": "ICMAI Syllabus 2022 Final Course Curriculum",
				"chapters": [
					{"title": "Cost and Management Audit", "lessons": ["Cost Audit Framework", "Cost Accounting Records", "Cost Audit Report", "Management Audit", "Internal Audit", "Operational Audit"]},
					{"title": "Corporate Financial Reporting", "lessons": ["Accounting Standards", "Consolidated Financial Statements", "Business Combinations", "Financial Instruments", "Integrated Reporting", "Government Accounting"]},
					{"title": "Indirect Tax Laws and Practice", "lessons": ["GST Levy and Collection", "Input Tax Credit", "Valuation", "Returns and Payment", "Refunds", "Customs Law"]},
					{"title": "Elective Papers", "lessons": ["Strategic Performance Management and Business Valuation", "Risk Management in Banking and Insurance", "Entrepreneurship and Startup"]},
				],
			},
		],
	},
	{
		"title": "CMA USA",
		"description": "Certified Management Accountant USA",
		"courses": [
			{
				"title": "CMA USA Part 1",
				"description": "Financial Planning, Performance, and Analytics.",
				"source": "IMA CMA Content Specification Overview",
				"chapters": [
					{"title": "External Financial Reporting Decisions", "lessons": ["Financial Statements", "Recognition and Measurement", "Valuation", "Disclosure Requirements"]},
					{"title": "Planning, Budgeting, and Forecasting", "lessons": ["Strategic Planning", "Budgeting Concepts", "Forecasting Techniques", "Annual Profit Plans"]},
					{"title": "Performance Management", "lessons": ["Cost and Variance Measures", "Responsibility Centers", "Performance Measures", "Balanced Scorecard"]},
					{"title": "Cost Management", "lessons": ["Measurement Concepts", "Costing Systems", "Overhead Costs", "Supply Chain Management", "Business Process Improvement"]},
					{"title": "Internal Controls", "lessons": ["Governance and Risk", "Internal Control Frameworks", "System Controls", "Compliance"]},
					{"title": "Technology and Analytics", "lessons": ["Information Systems", "Data Governance", "Data Analytics", "Technology Enabled Finance Transformation"]},
				],
			},
			{
				"title": "CMA USA Part 2",
				"description": "Strategic Financial Management.",
				"source": "IMA CMA Content Specification Overview",
				"chapters": [
					{"title": "Financial Statement Analysis", "lessons": ["Basic Financial Statement Analysis", "Financial Ratios", "Profitability Analysis", "Special Issues"]},
					{"title": "Corporate Finance", "lessons": ["Risk and Return", "Long Term Financial Management", "Capital Structure", "Working Capital Management"]},
					{"title": "Business Decision Analysis", "lessons": ["Cost Volume Profit Analysis", "Marginal Analysis", "Pricing Decisions", "Risk Assessment"]},
					{"title": "Enterprise Risk Management", "lessons": ["Risk Identification", "Risk Assessment", "Risk Mitigation", "Enterprise Risk Frameworks"]},
					{"title": "Capital Investment Decisions", "lessons": ["Capital Budgeting Process", "Discounted Cash Flow", "Payback and Accounting Rate of Return", "Risk in Capital Investments"]},
					{"title": "Professional Ethics", "lessons": ["Ethical Considerations", "IMA Statement of Ethical Professional Practice", "Fraud Triangle", "Resolving Ethical Issues"]},
				],
			},
		],
	},
	{
		"title": "CS",
		"description": "Company Secretary",
		"courses": [
			{
				"title": "CS CSEET",
				"description": "Company Secretary Executive Entrance Test.",
				"source": "ICSI CSEET Restructured Syllabus applicable from June 2026",
				"chapters": [
					{"title": "Business Communication", "lessons": ["Communication Basics", "English Grammar", "Business Correspondence", "Comprehension", "Presentation Skills"]},
					{"title": "Fundamentals of Accounting", "lessons": ["Accounting Principles", "Journal Entries", "Ledger Posting", "Trial Balance", "Final Accounts"]},
					{"title": "Economic and Business Environment", "lessons": ["Indian Economy", "Demand and Supply", "Business Environment", "Government Policies", "Entrepreneurship"]},
					{"title": "Business Laws and Management", "lessons": ["Indian Contract Act", "Sale of Goods", "Companies Act Basics", "Management Principles", "Planning and Organising"]},
				],
			},
			{
				"title": "CS Executive",
				"description": "Executive level for Company Secretary.",
				"source": "ICSI Executive Programme New Syllabus 2022",
				"chapters": [
					{"title": "Group 1", "lessons": ["Jurisprudence, Interpretation & General Laws", "Company Law & Practice", "Setting Up of Business, Industrial & Labour Laws", "Corporate Accounting & Financial Management"]},
					{"title": "Group 2", "lessons": ["Capital Market & Securities Laws", "Economic, Commercial & Intellectual Property Laws", "Tax Laws and Practice"]},
				],
			},
			{
				"title": "CS Professional",
				"description": "Professional level for Company Secretary.",
				"source": "ICSI Professional Programme New Syllabus 2022",
				"chapters": [
					{"title": "Group 1", "lessons": ["Environmental, Social and Governance Principles and Practice", "Drafting, Pleadings & Appearances", "Compliance Management, Audit & Due Diligence"]},
					{"title": "Elective 1", "lessons": ["CSR & Social Governance", "Internal & Forensic Audit", "Intellectual Property Rights - Law & Practice", "Artificial Intelligence, Data Analytics and Cyber Security", "Advanced Direct Tax Laws & Practice", "IFSCA Regulations, Listing and Compliances"]},
					{"title": "Group 2", "lessons": ["Strategic Management & Corporate Finance", "Corporate Restructuring, Valuation & Insolvency"]},
					{"title": "Elective 2", "lessons": ["Arbitration, Mediation & Conciliation", "Goods & Services Tax and Corporate Tax Planning", "Labour Laws & Practice", "Banking & Insurance Laws & Practice", "Insolvency and Bankruptcy Law & Practice"]},
				],
			},
		],
	},
	]

@frappe.whitelist()
def run_setup_script(script_name: str) -> str:
	"""Run predefined setup scripts to populate Course Groups."""
	frappe.only_for("System Manager")

	if script_name == "create_aptitude":
		_create_groups(APTITUDE_TEST_GROUPS)
		return "Aptitude Course Groups created or updated successfully."
	elif script_name == "create_higher_secondary":
		_create_program_course_groups(HIGHER_SECONDARY_ENTRANCE_PROGRAMS)
		return "Higher Secondary Entrance programs, course groups, courses, chapters, and lessons created or updated successfully."
	elif script_name == "create_higher_secondary_course_groups":
		_create_program_course_groups_only(HIGHER_SECONDARY_ENTRANCE_PROGRAMS)
		return "Higher Secondary Entrance Course Groups created or updated successfully."
	elif script_name == "create_professional":
		_create_professional_course_groups()
		return "CA course programs, course groups, courses, chapters, and lessons created or updated successfully."
	else:
		frappe.throw("Invalid setup script requested.")

def _create_groups(group_list: list[dict]) -> None:
	if not frappe.db.table_exists("Course Group"):
		frappe.throw("Course Group DocType not found. Please run migration first.")
	
	for group in group_list:
		if frappe.db.exists("Course Group", group["title"]):
			continue
		doc = frappe.new_doc("Course Group")
		doc.title = group["title"]
		doc.description = group["description"]
		doc.insert(ignore_permissions=True)
	
	frappe.db.commit()

def _create_professional_course_groups() -> None:
	_create_program_course_groups(PROFESSIONAL_PROGRAMS)

def _create_program_course_groups(programs: list[dict]) -> None:
	_validate_program_setup_doctypes()

	for program in programs:
		program_doc = _get_or_create_lms_program(program["title"], program["description"])
		program_course_names: list[str] = []

		for course in program["courses"]:
			group_doc = _get_or_create_course_group(course["title"], course["description"])
			course_name = _get_or_create_lms_course(
				title=course["title"],
				description=course["description"],
				course_group=group_doc.name,
			)
			_ensure_course_outline(
				course_name=course_name,
				chapters=course["chapters"],
				source=course["source"],
			)

			group_doc.set("courses", [{"course": course_name}])
			group_doc.save(ignore_permissions=True)
			program_course_names.append(course_name)

		program_doc.set("program_courses", [{"course": course_name} for course_name in program_course_names])
		program_doc.save(ignore_permissions=True)

	frappe.db.commit()

def _create_program_course_groups_only(programs: list[dict]) -> None:
	if not frappe.db.table_exists("Course Group"):
		frappe.throw("Course Group DocType not found. Please run migration first.")

	for program in programs:
		for course in program["courses"]:
			_get_or_create_course_group(course["title"], course["description"])

	frappe.db.commit()

def _validate_program_setup_doctypes() -> None:
	for doctype in ("Course Group", "LMS Program", "LMS Course", "Course Chapter", "Course Lesson"):
		if not frappe.db.table_exists(doctype):
			frappe.throw(f"{doctype} DocType not found. Please run migration first.")

def _get_or_create_course_group(title: str, description: str) -> Document:
	name = frappe.db.exists("Course Group", title)
	if name:
		return frappe.get_doc("Course Group", name)

	doc = frappe.new_doc("Course Group")
	doc.title = title
	doc.description = description
	doc.insert(ignore_permissions=True)
	return doc

def _get_or_create_lms_program(title: str, description: str) -> Document:
	name = frappe.db.get_value("LMS Program", {"title": title}, "name")
	if name:
		doc = frappe.get_doc("LMS Program", name)
		if not doc.published:
			doc.published = 1
		return doc

	doc = frappe.new_doc("LMS Program")
	doc.title = title
	doc.published = 1
	doc.insert(ignore_permissions=True)
	return doc

def _get_or_create_lms_course(title: str, description: str, course_group: str) -> str:
	name = frappe.db.get_value("LMS Course", {"title": title}, "name")
	if name:
		if not frappe.db.get_value("LMS Course", name, "published"):
			frappe.db.set_value("LMS Course", name, "published", 1, update_modified=False)
		if frappe.db.has_column("LMS Course", "course_group"):
			frappe.db.set_value("LMS Course", name, "course_group", course_group, update_modified=False)
		return name

	doc = frappe.new_doc("LMS Course")
	doc.title = title
	doc.short_introduction = description
	doc.description = description
	doc.published = 1
	doc.append("instructors", {"instructor": frappe.session.user})
	if frappe.db.has_column("LMS Course", "course_group"):
		doc.course_group = course_group
	doc.insert(ignore_permissions=True)
	return doc.name

def _ensure_course_outline(course_name: str, chapters: list[dict], source: str) -> None:
	chapter_names: list[str] = []
	course_title = frappe.db.get_value("LMS Course", course_name, "title")

	for chapter in chapters:
		chapter_name = _get_or_create_course_chapter(course_name, chapter["title"])
		chapter_names.append(chapter_name)
		chapter_doc = frappe.get_doc("Course Chapter", chapter_name)
		lesson_names = [
			_get_or_create_course_lesson(
				chapter_name=chapter_name,
				title=lesson_title,
				body=_get_lesson_body(lesson_title, chapter["title"], course_title, source),
			)
			for lesson_title in chapter["lessons"]
		]
		chapter_doc.set("lessons", [{"lesson": lesson_name} for lesson_name in lesson_names])
		chapter_doc.save(ignore_permissions=True)

	course_doc = frappe.get_doc("LMS Course", course_name)
	course_doc.set("chapters", [{"chapter": chapter_name} for chapter_name in chapter_names])
	course_doc.save(ignore_permissions=True)

def _get_or_create_course_chapter(course_name: str, title: str) -> str:
	name = frappe.db.get_value("Course Chapter", {"course": course_name, "title": title}, "name")
	if name:
		return name

	doc = frappe.new_doc("Course Chapter")
	doc.course = course_name
	doc.title = title
	doc.insert(ignore_permissions=True)
	return doc.name

def _get_or_create_course_lesson(chapter_name: str, title: str, body: str) -> str:
	name = frappe.db.get_value("Course Lesson", {"chapter": chapter_name, "title": title}, "name")
	if name:
		return name

	doc = frappe.new_doc("Course Lesson")
	doc.chapter = chapter_name
	doc.title = title
	doc.body = body
	doc.insert(ignore_permissions=True)
	return doc.name

def _get_lesson_body(lesson_title: str, chapter_title: str, course_title: str, source: str) -> str:
	return (
		f"# {lesson_title}\n\n"
		f"This lesson covers **{lesson_title}** under **{chapter_title}** for **{course_title}**.\n\n"
		f"Source syllabus: {source}.\n\n"
		"Key study focus:\n"
		f"- Understand the core concepts and terminology used in {lesson_title}.\n"
		f"- Learn how {lesson_title} is tested in the related professional exam paper.\n"
		f"- Practice exam-style problems and case scenarios connected to {chapter_title}.\n"
	)
