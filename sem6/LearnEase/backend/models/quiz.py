import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import re
import random
import os


# Load the fine-tuned model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "C:\\MProj\\LearnEase_New\\backend\\mcq_t5_finetuned1"  # Update with your model path
model = T5ForConditionalGeneration.from_pretrained(model_path).to(device)
tokenizer = T5Tokenizer.from_pretrained(model_path)

# Function to clean text and extract key phrases
def extract_key_answer(text):
    # First, check if there's a phrase with ||| which seems to be in your outputs
    if '|||' in text:
        parts = text.split('|||')
        if len(parts) > 1:
            return parts[1].strip()

    # Remove question marks and everything after them
    text = re.sub(r'\?.*$', '', text)

    # Simple sentence splitting (no NLTK dependency)
    sentences = [s.strip() for s in re.split(r'[.!;]', text) if s.strip()]
    if sentences:
        text = sentences[0].strip()

    # If text is too long, try to extract key noun phrases
    if len(text.split()) > 5:
        # Look for patterns that might contain the answer
        patterns = [
            r'is (?:the )?([^\.]+)',              # "is water cycle"
            r'called (?:the )?([^\.]+)',          # "called water cycle"
            r'known as (?:the )?([^\.]+)',        # "known as water cycle"
            r'termed (?:the )?([^\.]+)',          # "termed water cycle"
            r'(?:the )?([a-zA-Z ]+) (?:cycle|process)', # "water cycle" or "hydrologic cycle"
        ]

        for pattern in patterns:
            matches = re.search(pattern, text)
            if matches:
                return matches.group(1).strip()

    # If all else fails, just take the first 3-4 words
    words = text.split()
    if len(words) > 4:
        # Look for common scientific terms
        key_terms = ['water cycle', 'evaporation', 'condensation', 'precipitation',
                    'collection', 'hydrologic', 'hydrological']

        for term in key_terms:
            if term in text.lower():
                return term

        # Default to first few words
        return ' '.join(words[:3])

    return text

# Function to generate a question
def generate_question(text):
    input_text = f"Generate a single question from the following text: {text}"
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)

    output = model.generate(
        input_ids,
        max_length=50,
        do_sample=True,
        temperature=0.7
    )
    return tokenizer.decode(output[0], skip_special_tokens=True).strip()

# Function to parse the raw question output
def parse_question_output(raw_output):
    # Check if the output contains ||| which indicates the question and answer are combined
    if '|||' in raw_output:
        parts = raw_output.split('|||')

        # First part is the question
        question = parts[0].strip()

        # If there's a second part, it's likely the correct answer
        correct_answer = parts[1].strip() if len(parts) > 1 else ""

        # If there are more parts, they might be distractors
        distractors = [p.strip() for p in parts[2:] if p.strip()]

        return {
            "question": question,
            "correct_answer": correct_answer,
            "distractors": distractors
        }
    else:
        # If no ||| pattern, just return the question
        return {
            "question": raw_output,
            "correct_answer": "",
            "distractors": []
        }

# Create distractors manually if needed - IMPROVED to ensure uniqueness
def create_distractors(text, correct_answer, existing_distractors=None):
    # Start with any existing distractors
    distractors = [] if existing_distractors is None else existing_distractors.copy()

    # Clean up any trailing characters (like '|')
    distractors = [d.rstrip('| ') for d in distractors]

    # Predefined wrong answers related to water cycle
    water_cycle_distractors = {
        "water cycle": ["carbon cycle", "nitrogen cycle", "rock cycle", "life cycle",
                        "oxygen cycle", "phosphorus cycle", "nutrient cycle"],
        "evaporation": ["sublimation", "transpiration", "infiltration", "runoff",
                        "percolation", "radiation", "convection"],
        "condensation": ["precipitation", "collection", "purification", "filtration",
                         "distillation", "solidification", "vaporization"],
        "precipitation": ["evaporation", "collection", "condensation", "infiltration",
                          "accumulation", "distribution", "circulation"],
        "sun": ["moon", "gravity", "wind", "temperature", "pressure", "humidity", "atmosphere"],
        "clouds": ["fog", "mist", "steam", "humidity", "vapor", "rain", "snow"],
        "oceans": ["rivers", "lakes", "streams", "groundwater", "aquifers", "glaciers", "seas"],
        "collection": ["distribution", "circulation", "transportation", "purification",
                        "filtration", "absorption", "storage"],
         #-------------------------------------------------------------------------------------SCIENCE1-------------------------------------------------------------------------------------------------------:
        #chapter1
    "gravitation": ["gravity", "centripetal force", "gravitational force", "universal law", "mass", "weight", "acceleration"],
    "gravity": ["gravitational force", "magnetism", "buoyancy", "friction", "inertia", "momentum", "electrostatic force"],
    "centripetal force": ["centrifugal force", "gravitational force", "frictional force", "tension", "normal force", "spring force", "applied force"],
    "centrifugal force": ["centripetal force", "gravitational force", "tension", "elastic force", "friction", "buoyant force", "drag"],
    "Newton's laws": ["Kepler's laws", "Boyle's law", "law of conservation", "Ohm's law", "Hooke's law", "Faraday's law", "thermodynamics laws"],
    "Kepler's laws": ["Newton's laws", "law of inertia", "law of motion", "law of gravitation", "Pascal's law", "Bernoulli's law", "Archimedes' principle"],
    "free fall": ["projectile motion", "circular motion", "linear motion", "oscillatory motion", "random motion", "relative motion", "translational motion"],
    "acceleration due to gravity": ["gravitational constant", "centripetal acceleration", "tangential acceleration", "angular acceleration", "linear acceleration", "terminal velocity", "drift velocity"],
    "mass": ["weight", "density", "volume", "pressure", "momentum", "force", "energy"],
    "weight": ["mass", "gravitational force", "normal force", "tension", "frictional force", "buoyant force", "electrostatic force"],
    "gravitational potential energy": ["kinetic energy", "elastic potential energy", "chemical energy", "nuclear energy", "thermal energy", "magnetic energy", "light energy"],
    "kinetic energy": ["potential energy", "mechanical energy", "heat energy", "nuclear energy", "chemical energy", "wave energy", "elastic energy"],
    "escape velocity": ["orbital velocity", "terminal velocity", "average velocity", "drift velocity", "tangential velocity", "instantaneous velocity", "sound velocity"],
    "orbital velocity": ["angular velocity", "linear velocity", "escape velocity", "tangential velocity", "terminal velocity", "wave velocity", "relative velocity"],
    "satellite": ["planet", "moon", "asteroid", "comet", "meteor", "star", "galaxy"],
    "artificial satellite": ["natural satellite", "space probe", "space station", "rover", "lander", "orbiter", "spaceship"],
    "natural satellite": ["artificial satellite", "comet", "asteroid", "star", "nebula", "galaxy", "dwarf planet"],
    "geostationary orbit": ["polar orbit", "low Earth orbit", "high Earth orbit", "circular orbit", "elliptical orbit", "heliosynchronous orbit", "retrograde orbit"],
    "low Earth orbit": ["medium Earth orbit", "geostationary orbit", "elliptical orbit", "circular orbit", "heliocentric orbit", "translunar orbit", "asteroidal orbit"],
    "microgravity": ["zero gravity", "free fall", "weightlessness", "buoyancy", "magnetism", "inertia", "radiation pressure"],
    "trajectory": ["orbit", "course", "flight path", "route", "vector", "arc", "slope"],
    "orbital period": ["rotation period", "revolution period", "synodic period", "sidereal period", "solar day", "lunar day", "stellar day"],
    "angular velocity": ["linear velocity", "orbital velocity", "tangential velocity", "escape velocity", "terminal velocity", "average velocity", "instantaneous velocity"],
    "terminal velocity": ["escape velocity", "average velocity", "instantaneous velocity", "relative velocity", "angular velocity", "tangential velocity", "drift velocity"],
    "momentum": ["inertia", "impulse", "force", "acceleration", "work", "power", "torque"],
    "inertia": ["mass", "momentum", "energy", "force", "velocity", "impulse", "work"],
    "force": ["pressure", "torque", "momentum", "energy", "work", "impulse", "power"],
    "pressure": ["force", "density", "momentum", "energy", "area", "acceleration", "torque"],
    "torque": ["force", "momentum", "pressure", "impulse", "power", "work", "angular velocity"],
    "impulse": ["momentum", "force", "torque", "acceleration", "velocity", "power", "energy"],
    "velocity": ["speed", "acceleration", "momentum", "impulse", "torque", "displacement", "angular velocity"],
    "displacement": ["velocity", "acceleration", "distance", "work", "momentum", "force", "torque"],
    "acceleration": ["velocity", "force", "momentum", "work", "impulse", "torque", "displacement"],
    "work": ["energy", "power", "momentum", "torque", "impulse", "velocity", "acceleration"],
    "energy": ["work", "power", "momentum", "torque", "impulse", "velocity", "acceleration"],
    "power": ["energy", "work", "torque", "impulse", "velocity", "momentum", "acceleration"],
    "buoyancy": ["pressure", "force", "gravity", "momentum", "impulse", "torque", "density"],
    "density": ["mass", "volume", "pressure", "force", "gravity", "impulse", "momentum"],
    "universal law of gravitation": ["Kepler’s laws", "Newton’s laws", "law of inertia", "law of conservation", "law of motion", "law of force", "law of acceleration"],
    "centripetal acceleration": ["tangential acceleration", "angular acceleration", "linear acceleration", "escape velocity", "terminal velocity", "orbital velocity", "drift velocity"],
    "Newton’s first law": ["law of inertia", "law of motion", "law of universal gravitation", "law of conservation", "law of energy", "Boyle’s law", "Hooke’s law"],
    "Newton’s second law": ["law of acceleration", "law of force", "law of momentum", "law of inertia", "law of friction", "law of energy", "law of conservation"],
    "Newton’s third law": ["law of action-reaction", "law of equal and opposite reaction", "law of force pairs", "law of motion", "law of interaction", "law of equilibrium", "law of conservation"],
    #chapter2
    "periodic table": ["modern periodic table", "Mendeleev's periodic table", "Dobereiner’s triads", "Newlands' law", "atomic structure", "chemical bonding", "electronegativity"],
    "Mendeleev's periodic table": ["modern periodic table", "Newlands' law", "atomic theory", "Bohr’s model", "quantum theory", "reactivity series", "electrochemistry"],
    "modern periodic table": ["Mendeleev's periodic table", "Newlands' law", "periodic law", "atomic structure", "electron configuration", "stoichiometry", "valency"],
    "atomic number": ["mass number", "atomic mass", "molar mass", "isotopes", "ionization energy", "electronegativity", "covalency"],
    "atomic mass": ["atomic number", "molar mass", "isotopes", "relative atomic mass", "ionization energy", "proton number", "electron affinity"],
    "groups": ["periods", "blocks", "series", "subshells", "orbitals", "valence shells", "families"],
    "periods": ["groups", "blocks", "orbitals", "subshells", "energy levels", "atomic orbitals", "series"],
    "valency": ["oxidation state", "covalency", "electron affinity", "electronegativity", "ionization energy", "reducing power", "atomic radius"],
    "electronegativity": ["ionization energy", "electron affinity", "valency", "oxidation state", "atomic radius", "bond energy", "reactivity"],
    "ionization energy": ["electron affinity", "electronegativity", "oxidation potential", "reduction potential", "bond energy", "atomic radius", "nuclear charge"],
    "electron affinity": ["ionization energy", "electronegativity", "atomic radius", "oxidation state", "bond energy", "covalent bond", "metallic bond"],
    "atomic radius": ["ionic radius", "covalent radius", "van der Waals radius", "electronegativity", "bond length", "molecular radius", "energy level"],
    "metallic character": ["non-metallic character", "reactivity", "ionization energy", "electron affinity", "oxidation state", "electronegativity", "atomic radius"],
    "non-metallic character": ["metallic character", "reactivity", "ionization energy", "oxidation state", "covalency", "electronegativity", "atomic size"],
    "lanthanides": ["actinides", "transition metals", "alkali metals", "halogens", "noble gases", "alkaline earth metals", "post-transition metals"],
    "actinides": ["lanthanides", "transition metals", "noble gases", "alkali metals", "halogens", "alkaline earth metals", "post-transition metals"],
    "transition metals": ["alkali metals", "alkaline earth metals", "post-transition metals", "metalloids", "halogens", "noble gases", "lanthanides"],
    "alkali metals": ["alkaline earth metals", "transition metals", "metalloids", "halogens", "noble gases", "lanthanides", "actinides"],
    "alkaline earth metals": ["alkali metals", "transition metals", "metalloids", "halogens", "noble gases", "lanthanides", "actinides"],
    "halogens": ["noble gases", "alkali metals", "transition metals", "alkaline earth metals", "metalloids", "post-transition metals", "actinides"],
    "noble gases": ["halogens", "alkali metals", "transition metals", "alkaline earth metals", "metalloids", "post-transition metals", "actinides"],
    "oxidation state": ["valency", "oxidation potential", "reduction potential", "electron affinity", "electronegativity", "ionization energy", "bond energy"],
    "isotopes": ["isobars", "ions", "electrons", "protons", "neutrons", "cations", "anions"],
    "isobars": ["isotopes", "ions", "cations", "anions", "neutrons", "protons", "electrons"],
    "ions": ["isotopes", "isobars", "cations", "anions", "electrons", "protons", "neutrons"],
    "cations": ["anions", "ions", "isotopes", "isobars", "neutrons", "protons", "electrons"],
    "anions": ["cations", "ions", "isotopes", "isobars", "neutrons", "protons", "electrons"],
    "metalloids": ["transition metals", "post-transition metals", "alkali metals", "alkaline earth metals", "halogens", "noble gases", "actinides"],
    "post-transition metals": ["transition metals", "metalloids", "alkali metals", "alkaline earth metals", "halogens", "noble gases", "actinides"],
    "Moseley's law": ["Mendeleev’s periodic law", "Newlands’ law", "Dalton’s atomic theory", "Bohr’s model", "quantum mechanics", "atomic structure", "electron configuration"],
    "Newlands’ law": ["Mendeleev’s periodic law", "Moseley’s law", "Dalton’s atomic theory", "Bohr’s model", "quantum mechanics", "atomic structure", "electron configuration"],
    "Dobereiner's triads": ["Newlands' law", "Mendeleev’s periodic law", "Moseley’s law", "Bohr’s model", "quantum mechanics", "atomic structure", "electron configuration"],
    "periodic law": ["modern periodic table", "Mendeleev’s periodic table", "Newlands' law", "atomic structure", "electron configuration", "stoichiometry", "valency"],
    "electronic configuration": ["electron affinity", "ionization energy", "electronegativity", "oxidation state", "bond energy", "atomic radius", "nuclear charge"],
    "bond energy": ["ionization energy", "electron affinity", "electronegativity", "oxidation state", "covalent bond", "metallic bond", "van der Waals forces"],
    "covalent bond": ["ionic bond", "metallic bond", "hydrogen bond", "dipole-dipole interaction", "van der Waals forces", "London dispersion force", "polar bond"],
    "ionic bond": ["covalent bond", "metallic bond", "hydrogen bond", "dipole-dipole interaction", "van der Waals forces", "London dispersion force", "polar bond"],
    "metallic bond": ["ionic bond", "covalent bond", "hydrogen bond", "dipole-dipole interaction", "van der Waals forces", "London dispersion force", "polar bond"],
    "hydrogen bond": ["ionic bond", "covalent bond", "metallic bond", "dipole-dipole interaction", "van der Waals forces", "London dispersion force", "polar bond"],
    "periodic trends": ["electronegativity", "ionization energy", "electron affinity", "oxidation state", "atomic radius", "bond energy", "reactivity"],
     #chapter3

    "chemical reaction": ["physical change", "nuclear reaction", "combustion", "fusion", "decomposition", "sublimation", "oxidation"],
    "chemical equation": ["chemical formula", "empirical formula", "molecular equation", "stoichiometric equation", "balanced equation", "structural formula", "reaction mechanism"],
    "reactants": ["products", "catalysts", "solvents", "electrolytes", "precipitates", "spectators", "substrates"],
    "products": ["reactants", "catalysts", "solvents", "electrolytes", "precipitates", "spectators", "substrates"],
    "balanced equation": ["unbalanced equation", "empirical formula", "molecular formula", "reaction mechanism", "stoichiometry", "ionic equation", "word equation"],
    "stoichiometry": ["molecular weight", "empirical formula", "reaction kinetics", "catalysis", "thermodynamics", "enthalpy", "activation energy"],
    "combustion reaction": ["decomposition reaction", "displacement reaction", "double displacement reaction", "neutralization", "oxidation", "precipitation", "fermentation"],
    "decomposition reaction": ["combustion reaction", "displacement reaction", "neutralization", "synthesis reaction", "polymerization", "oxidation", "fermentation"],
    "displacement reaction": ["combustion reaction", "decomposition reaction", "neutralization", "synthesis reaction", "polymerization", "oxidation", "fermentation"],
    "double displacement reaction": ["combustion reaction", "decomposition reaction", "displacement reaction", "synthesis reaction", "polymerization", "oxidation", "fermentation"],
    "oxidation": ["reduction", "neutralization", "hydrolysis", "esterification", "saponification", "sublimation", "polymerization"],
    "reduction": ["oxidation", "neutralization", "hydrolysis", "esterification", "saponification", "sublimation", "polymerization"],
    "oxidizing agent": ["reducing agent", "catalyst", "electrolyte", "precipitate", "emulsifier", "coagulating agent", "buffer"],
    "reducing agent": ["oxidizing agent", "catalyst", "electrolyte", "precipitate", "emulsifier", "coagulating agent", "buffer"],
    "catalyst": ["inhibitor", "oxidizing agent", "reducing agent", "solvent", "buffer", "precipitate", "adsorbent"],
    "precipitate": ["solvent", "buffer", "oxidizing agent", "reducing agent", "adsorbent", "electrolyte", "solution"],
    "exothermic reaction": ["endothermic reaction", "oxidation", "reduction", "neutralization", "sublimation", "adsorption", "decomposition"],
    "endothermic reaction": ["exothermic reaction", "oxidation", "reduction", "neutralization", "sublimation", "adsorption", "decomposition"],
    "neutralization reaction": ["oxidation", "reduction", "combustion", "decomposition", "fermentation", "precipitation", "polymerization"],
    "corrosion": ["rusting", "oxidation", "tarnishing", "electroplating", "deposition", "sublimation", "diffusion"],
    "rusting": ["corrosion", "oxidation", "tarnishing", "electroplating", "deposition", "sublimation", "diffusion"],
    "electroplating": ["galvanization", "rusting", "oxidation", "tarnishing", "precipitation", "diffusion", "corrosion"],
    "alloy": ["mixture", "compound", "solution", "suspension", "colloid", "precipitate", "emulsion"],
    "hydrolysis": ["oxidation", "reduction", "neutralization", "fermentation", "combustion", "adsorption", "polymerization"],
    "saponification": ["neutralization", "hydrolysis", "oxidation", "reduction", "fermentation", "precipitation", "adsorption"],
    "fermentation": ["combustion", "oxidation", "reduction", "neutralization", "polymerization", "adsorption", "hydrolysis"],
    "adsorption": ["absorption", "neutralization", "oxidation", "reduction", "fermentation", "precipitation", "hydrolysis"],
    "absorption": ["adsorption", "neutralization", "oxidation", "reduction", "fermentation", "precipitation", "hydrolysis"],
    "polymerization": ["oxidation", "reduction", "neutralization", "fermentation", "combustion", "adsorption", "hydrolysis"],
    "activation energy": ["bond energy", "potential energy", "kinetic energy", "heat of reaction", "enthalpy", "entropy", "catalysis"],
    "bond energy": ["activation energy", "potential energy", "kinetic energy", "heat of reaction", "enthalpy", "entropy", "catalysis"],
    "heat of reaction": ["activation energy", "bond energy", "potential energy", "kinetic energy", "enthalpy", "entropy", "catalysis"],
    "enthalpy": ["entropy", "activation energy", "bond energy", "potential energy", "kinetic energy", "heat of reaction", "catalysis"],
    "entropy": ["enthalpy", "activation energy", "bond energy", "potential energy", "kinetic energy", "heat of reaction", "catalysis"],
    "redox reaction": ["oxidation", "reduction", "combustion", "neutralization", "fermentation", "polymerization", "hydrolysis"],
    "electrolysis": ["electroplating", "oxidation", "reduction", "neutralization", "fermentation", "precipitation", "adsorption"],
    "reaction rate": ["reaction mechanism", "equilibrium constant", "activation energy", "bond energy", "enthalpy", "entropy", "stoichiometry"],
    "catalysis": ["activation energy", "reaction rate", "reaction mechanism", "equilibrium constant", "enthalpy", "entropy", "stoichiometry"],
    "reaction mechanism": ["reaction rate", "equilibrium constant", "activation energy", "bond energy", "enthalpy", "entropy", "stoichiometry"],
    "equilibrium constant": ["reaction mechanism", "reaction rate", "activation energy", "bond energy", "enthalpy", "entropy", "stoichiometry"],
    "buffer solution": ["electrolyte", "catalyst", "precipitate", "adsorbent", "solution", "colloid", "suspension"],
    "chemical kinetics": ["reaction rate", "reaction mechanism", "equilibrium constant", "activation energy", "bond energy", "enthalpy", "entropy"],
    "collision theory": ["reaction rate", "reaction mechanism", "equilibrium constant", "activation energy", "bond energy", "enthalpy", "entropy"],
     #chapter4

    "electric current": ["voltage", "power", "energy", "resistance", "capacitance", "magnetism", "induction"],
    "voltage": ["current", "power", "resistance", "inductance", "capacitance", "frequency", "conductance"],
    "resistance": ["impedance", "conductance", "inductance", "capacitance", "reactance", "power", "voltage"],
    "Ohm's law": ["Kirchhoff's law", "Lenz's law", "Faraday's law", "Ampere's law", "Coulomb's law", "Newton's law", "Kepler's law"],
    "series circuit": ["parallel circuit", "short circuit", "open circuit", "resonant circuit", "balanced circuit", "power circuit", "inductive circuit"],
    "parallel circuit": ["series circuit", "short circuit", "open circuit", "resonant circuit", "balanced circuit", "power circuit", "inductive circuit"],
    "electric power": ["electric energy", "voltage", "current", "capacitance", "resistance", "impedance", "reactance"],
    "electric energy": ["electric power", "voltage", "current", "capacitance", "resistance", "impedance", "reactance"],
    "joule’s law": ["Ohm's law", "Kirchhoff’s law", "Faraday’s law", "Lenz’s law", "Coulomb’s law", "Newton’s law", "Kepler’s law"],
    "heating effect": ["magnetic effect", "inductive effect", "resistive effect", "photoelectric effect", "thermionic effect", "piezoelectric effect", "capacitive effect"],
    "fuse": ["circuit breaker", "resistor", "capacitor", "transistor", "inductor", "relay", "diode"],
    "circuit breaker": ["fuse", "resistor", "capacitor", "transistor", "inductor", "relay", "diode"],
    "electric motor": ["generator", "transformer", "alternator", "rectifier", "capacitor", "diode", "relay"],
    "generator": ["electric motor", "transformer", "alternator", "rectifier", "capacitor", "diode", "relay"],
    "electromagnet": ["permanent magnet", "diamagnet", "paramagnet", "ferromagnet", "superconductor", "transformer", "coil"],
    "magnetic field": ["electric field", "gravitational field", "thermal field", "optical field", "acoustic field", "pressure field", "plasma field"],
    "solenoid": ["coil", "electromagnet", "resistor", "capacitor", "inductor", "transformer", "diode"],
    "inductor": ["capacitor", "resistor", "transformer", "diode", "relay", "transistor", "semiconductor"],
    "transformer": ["rectifier", "capacitor", "inductor", "motor", "generator", "diode", "relay"],
    "alternating current": ["direct current", "static electricity", "induced current", "eddy current", "pulsed current", "resonant current", "magnetized current"],
    "direct current": ["alternating current", "static electricity", "induced current", "eddy current", "pulsed current", "resonant current", "magnetized current"],
    "induced current": ["alternating current", "direct current", "static electricity", "eddy current", "pulsed current", "resonant current", "magnetized current"],
    "eddy currents": ["induced currents", "static electricity", "pulsed currents", "resonant currents", "magnetized currents", "surface currents", "electrostatic currents"],
    "magnetic effect": ["heating effect", "electrostatic effect", "resistive effect", "photoelectric effect", "thermionic effect", "piezoelectric effect", "capacitive effect"],
    "Lenz’s law": ["Faraday’s law", "Ohm’s law", "Kirchhoff’s law", "Ampere’s law", "Coulomb’s law", "Newton’s law", "Kepler’s law"],
    "Faraday’s law": ["Lenz’s law", "Ohm’s law", "Kirchhoff’s law", "Ampere’s law", "Coulomb’s law", "Newton’s law", "Kepler’s law"],
    "Ampere’s law": ["Faraday’s law", "Lenz’s law", "Ohm’s law", "Kirchhoff’s law", "Coulomb’s law", "Newton’s law", "Kepler’s law"],
    "Kirchhoff’s law": ["Ohm’s law", "Lenz’s law", "Faraday’s law", "Ampere’s law", "Coulomb’s law", "Newton’s law", "Kepler’s law"],
    "Coulomb’s law": ["Ohm’s law", "Lenz’s law", "Faraday’s law", "Ampere’s law", "Kirchhoff’s law", "Newton’s law", "Kepler’s law"],
    "static electricity": ["electric current", "induced current", "eddy currents", "pulsed currents", "resonant currents", "magnetized currents", "electrostatic currents"],
    "electromagnetic induction": ["self-induction", "mutual induction", "electrostatic induction", "photoelectric effect", "thermoelectric effect", "piezoelectric effect", "capacitive effect"],
    "self-induction": ["mutual induction", "electromagnetic induction", "electrostatic induction", "photoelectric effect", "thermoelectric effect", "piezoelectric effect", "capacitive effect"],
    "mutual induction": ["self-induction", "electromagnetic induction", "electrostatic induction", "photoelectric effect", "thermoelectric effect", "piezoelectric effect", "capacitive effect"],
    "rectifier": ["transformer", "capacitor", "inductor", "motor", "generator", "diode", "relay"],
    "diode": ["rectifier", "capacitor", "inductor", "motor", "generator", "transistor", "relay"],
    "transistor": ["rectifier", "capacitor", "inductor", "motor", "generator", "diode", "relay"],
    "relay": ["rectifier", "capacitor", "inductor", "motor", "generator", "diode", "transistor"],
    "semiconductor": ["conductor", "insulator", "superconductor", "resistor", "capacitor", "diode", "transistor"],
    "superconductor": ["conductor", "insulator", "semiconductor", "resistor", "capacitor", "diode", "transistor"],
    "electromagnetic wave": ["radio wave", "microwave", "infrared wave", "visible wave", "ultraviolet wave", "X-ray", "gamma ray"],
    "electromagnetic spectrum": ["infrared spectrum", "visible spectrum", "ultraviolet spectrum", "X-ray spectrum", "gamma-ray spectrum", "radio spectrum", "microwave spectrum"],
     #chapter5

    "magnetic field": ["electric field", "gravitational field", "thermal field", "acoustic field", "pressure field", "plasma field", "optical field"],
    "magnetism": ["electrostatics", "induction", "resistance", "capacitance", "radiation", "wave propagation", "conduction"],
    "electromagnetism": ["electrostatics", "thermodynamics", "gravitation", "fluid dynamics", "quantum mechanics", "radioactivity", "chemical bonding"],
    "magnet": ["electromagnet", "superconductor", "resistor", "capacitor", "diode", "transistor", "insulator"],
    "bar magnet": ["horseshoe magnet", "ring magnet", "cylindrical magnet", "electromagnet", "superconductor", "paramagnet", "diamagnet"],
    "poles of a magnet": ["magnetic field lines", "magnetic induction", "magnetic dipole", "magnetic moment", "magnetization", "flux density", "permeability"],
    "magnetic field lines": ["electric field lines", "equipotential lines", "wavefronts", "isobars", "isotherms", "contour lines", "stress lines"],
    "north pole": ["south pole", "neutral point", "dipole", "magnetic axis", "equatorial region", "positive charge", "negative charge"],
    "south pole": ["north pole", "neutral point", "dipole", "magnetic axis", "equatorial region", "positive charge", "negative charge"],
    "magnetic dipole": ["electric dipole", "thermal dipole", "gravitational dipole", "resonance", "quantum state", "molecular bond", "wave-particle duality"],
    "magnetic induction": ["electrostatic induction", "self-induction", "mutual induction", "photoelectric effect", "thermoelectric effect", "piezoelectric effect", "capacitive effect"],
    "magnetization": ["polarization", "ionization", "excitation", "conduction", "radiation", "diffusion", "absorption"],
    "magnetic moment": ["electric moment", "dipole moment", "polar moment", "angular momentum", "linear momentum", "torque", "resistance"],
    "permeability": ["permittivity", "resistivity", "conductivity", "susceptibility", "capacitance", "inductance", "impedance"],
    "magnetic flux": ["electric flux", "heat flux", "fluid flux", "mass flux", "wave flux", "energy flux", "momentum flux"],
    "right-hand thumb rule": ["left-hand rule", "Fleming’s right-hand rule", "Fleming’s left-hand rule", "corkscrew rule", "Lorentz force", "Lenz’s law", "Newton’s law"],
    "Fleming’s right-hand rule": ["Fleming’s left-hand rule", "right-hand thumb rule", "left-hand rule", "Lorentz force", "Lenz’s law", "Maxwell’s equation", "Faraday’s law"],
    "Fleming’s left-hand rule": ["Fleming’s right-hand rule", "right-hand thumb rule", "left-hand rule", "Lorentz force", "Lenz’s law", "Maxwell’s equation", "Faraday’s law"],
    "Lorentz force": ["Coulomb force", "gravitational force", "nuclear force", "frictional force", "centripetal force", "normal force", "tension force"],
    "solenoid": ["inductor", "capacitor", "resistor", "transformer", "diode", "rectifier", "transistor"],
    "torroid": ["solenoid", "coil", "cylindrical magnet", "bar magnet", "horseshoe magnet", "electromagnet", "permanent magnet"],
    "electromagnet": ["permanent magnet", "paramagnet", "diamagnet", "superconductor", "resistor", "capacitor", "inductor"],
    "hysteresis": ["inductance", "capacitance", "resistance", "susceptibility", "coercivity", "permittivity", "conductance"],
    "induced current": ["static electricity", "eddy currents", "pulsed currents", "resonant currents", "magnetized currents", "surface currents", "electrostatic currents"],
    "eddy currents": ["induced currents", "static electricity", "pulsed currents", "resonant currents", "magnetized currents", "surface currents", "electrostatic currents"],
    "self-induction": ["mutual induction", "electrostatic induction", "electromagnetic induction", "photoelectric effect", "thermoelectric effect", "piezoelectric effect", "capacitive effect"],
    "mutual induction": ["self-induction", "electromagnetic induction", "electrostatic induction", "photoelectric effect", "thermoelectric effect", "piezoelectric effect", "capacitive effect"],
    "generator": ["electric motor", "transformer", "alternator", "rectifier", "capacitor", "diode", "relay"],
    "electric motor": ["generator", "transformer", "alternator", "rectifier", "capacitor", "diode", "relay"],
    "AC generator": ["DC generator", "step-up transformer", "step-down transformer", "rectifier", "oscillator", "inductor", "resistor"],
    "DC motor": ["AC motor", "step-up transformer", "step-down transformer", "rectifier", "oscillator", "inductor", "resistor"],
    "commutator": ["diode", "capacitor", "inductor", "resistor", "rectifier", "oscillator", "transformer"],
    "brushes": ["contacts", "armature", "field coil", "stator", "rotor", "windings", "commutator"],
    "armature": ["rotor", "stator", "field coil", "brushes", "windings", "commutator", "diode"],
    "rotor": ["stator", "armature", "field coil", "brushes", "windings", "commutator", "diode"],
    "stator": ["rotor", "armature", "field coil", "brushes", "windings", "commutator", "diode"],
    "magnetic field strength": ["electric field strength", "intensity", "force", "capacitance", "inductance", "resistance", "conductance"],
    "electromagnetic waves": ["radio waves", "microwaves", "infrared waves", "visible light", "ultraviolet waves", "X-rays", "gamma rays"],
    "electromagnetic spectrum": ["infrared spectrum", "visible spectrum", "ultraviolet spectrum", "X-ray spectrum", "gamma-ray spectrum", "radio spectrum", "microwave spectrum"],
    "transformer": ["rectifier", "capacitor", "inductor", "motor", "generator", "diode", "relay"],
    "step-up transformer": ["step-down transformer", "AC motor", "DC motor", "rectifier", "oscillator", "inductor", "resistor"],
    "step-down transformer": ["step-up transformer", "AC motor", "DC motor", "rectifier", "oscillator", "inductor", "resistor"],
        #chapter6

    "refraction": ["reflection", "diffraction", "dispersion", "scattering", "absorption", "polarization", "interference"],
    "light": ["sound", "heat", "electricity", "magnetism", "radio waves", "X-rays", "microwaves"],
    "incident ray": ["reflected ray", "refracted ray", "emergent ray", "parallel ray", "normal ray", "diverging ray", "converging ray"],
    "refracted ray": ["incident ray", "reflected ray", "emergent ray", "parallel ray", "normal ray", "diverging ray", "converging ray"],
    "normal": ["tangent", "perpendicular", "parallel", "bisector", "radius", "chord", "secant"],
    "angle of incidence": ["angle of refraction", "angle of deviation", "angle of emergence", "angle of dispersion", "critical angle", "angle of polarization", "angle of diffraction"],
    "angle of refraction": ["angle of incidence", "angle of deviation", "angle of emergence", "angle of dispersion", "critical angle", "angle of polarization", "angle of diffraction"],
    "laws of refraction": ["laws of reflection", "laws of diffraction", "laws of thermodynamics", "Newton’s laws", "laws of motion", "Ohm’s law", "Snell’s law"],
    "Snell’s law": ["Newton’s law", "Ohm’s law", "Boyle’s law", "Kirchhoff’s law", "Kepler’s law", "Faraday’s law", "Lenz’s law"],
    "refractive index": ["optical density", "electrical resistance", "thermal conductivity", "specific heat", "wavelength", "frequency", "power"],
    "optical density": ["refractive index", "specific gravity", "electrical density", "thermal capacity", "mass density", "surface tension", "elasticity"],
    "critical angle": ["angle of refraction", "angle of incidence", "angle of emergence", "angle of deviation", "polarization angle", "diffraction angle", "scattering angle"],
    "total internal reflection": ["diffraction", "dispersion", "polarization", "scattering", "absorption", "interference", "fluorescence"],
    "real image": ["virtual image", "diminished image", "magnified image", "inverted image", "erect image", "diffused image", "shadow"],
    "virtual image": ["real image", "diminished image", "magnified image", "inverted image", "erect image", "diffused image", "shadow"],
    "lens": ["mirror", "prism", "plane glass", "diffuser", "polarizer", "conductor", "filter"],
    "convex lens": ["concave lens", "concave mirror", "convex mirror", "prism", "plane mirror", "cylindrical lens", "spherical lens"],
    "concave lens": ["convex lens", "concave mirror", "convex mirror", "prism", "plane mirror", "cylindrical lens", "spherical lens"],
    "converging lens": ["diverging lens", "convex mirror", "concave mirror", "flat mirror", "prism", "polarizer", "diffuser"],
    "diverging lens": ["converging lens", "convex mirror", "concave mirror", "flat mirror", "prism", "polarizer", "diffuser"],
    "focal point": ["optical center", "pole", "principal axis", "vertex", "center of curvature", "edge", "periphery"],
    "optical center": ["focal point", "pole", "principal axis", "vertex", "center of curvature", "edge", "periphery"],
    "principal axis": ["secondary axis", "focal axis", "polar axis", "radial axis", "tangent line", "perpendicular line", "diagonal line"],
    "focal length": ["wavelength", "amplitude", "frequency", "time period", "optical density", "mass density", "surface tension"],
    "power of lens": ["focal length", "optical density", "refractive index", "light intensity", "wavelength", "frequency", "transmittance"],
    "convex mirror": ["concave mirror", "concave lens", "convex lens", "plane mirror", "prism", "diffuser", "polarizer"],
    "concave mirror": ["convex mirror", "concave lens", "convex lens", "plane mirror", "prism", "diffuser", "polarizer"],
    "mirror formula": ["lens formula", "Snell’s law", "Ohm’s law", "Newton’s law", "Kirchhoff’s law", "Boyle’s law", "Faraday’s law"],
    "lens formula": ["mirror formula", "Snell’s law", "Ohm’s law", "Newton’s law", "Kirchhoff’s law", "Boyle’s law", "Faraday’s law"],
    "magnification": ["power", "resolution", "refraction", "reflection", "intensity", "luminosity", "spectrum"],
    "ray diagram": ["circuit diagram", "flowchart", "histogram", "graph", "table", "block diagram", "scatter plot"],
    "accommodation of eye": ["myopia", "hypermetropia", "presbyopia", "astigmatism", "cataract", "glaucoma", "corneal opacity"],
    "myopia": ["hypermetropia", "presbyopia", "astigmatism", "cataract", "glaucoma", "color blindness", "night blindness"],
    "hypermetropia": ["myopia", "presbyopia", "astigmatism", "cataract", "glaucoma", "color blindness", "night blindness"],
    "presbyopia": ["myopia", "hypermetropia", "astigmatism", "cataract", "glaucoma", "color blindness", "night blindness"],
    "astigmatism": ["myopia", "hypermetropia", "presbyopia", "cataract", "glaucoma", "color blindness", "night blindness"],
    "cataract": ["glaucoma", "myopia", "hypermetropia", "presbyopia", "astigmatism", "color blindness", "night blindness"],
    "glaucoma": ["cataract", "myopia", "hypermetropia", "presbyopia", "astigmatism", "color blindness", "night blindness"],
    "prism": ["mirror", "lens", "polarizer", "diffuser", "conductor", "capacitor", "resistor"],
    "dispersion": ["refraction", "reflection", "scattering", "diffraction", "absorption", "polarization", "interference"],
    "rainbow": ["halo", "mirage", "eclipse", "constellation", "aurora", "glow", "shadow"],
    "optical fiber": ["copper wire", "aluminum wire", "semiconductor", "conductor", "dielectric", "inductor", "resistor"],
    "binoculars": ["telescope", "microscope", "periscope", "kaleidoscope", "magnifying glass", "camera", "prism"],
    "telescope": ["microscope", "periscope", "binoculars", "camera", "projector", "laser", "mirror"],
    "microscope": ["telescope", "periscope", "binoculars", "camera", "projector", "laser", "mirror"],
        #chapter7

    "lens": ["mirror", "prism", "plane glass", "diffuser", "polarizer", "conductor", "filter"],
    "convex lens": ["concave lens", "concave mirror", "convex mirror", "prism", "plane mirror", "cylindrical lens", "spherical lens"],
    "concave lens": ["convex lens", "concave mirror", "convex mirror", "prism", "plane mirror", "cylindrical lens", "spherical lens"],
    "principal axis": ["secondary axis", "focal axis", "polar axis", "radial axis", "tangent line", "perpendicular line", "diagonal line"],
    "optical center": ["focal point", "pole", "principal axis", "vertex", "center of curvature", "edge", "periphery"],
    "focal point": ["optical center", "pole", "principal axis", "vertex", "center of curvature", "edge", "periphery"],
    "focal length": ["wavelength", "amplitude", "frequency", "time period", "optical density", "mass density", "surface tension"],
    "converging lens": ["diverging lens", "convex mirror", "concave mirror", "flat mirror", "prism", "polarizer", "diffuser"],
    "diverging lens": ["converging lens", "convex mirror", "concave mirror", "flat mirror", "prism", "polarizer", "diffuser"],
    "image formation": ["light reflection", "light absorption", "scattering", "interference", "diffraction", "dispersion", "polarization"],
    "real image": ["virtual image", "diminished image", "magnified image", "inverted image", "erect image", "diffused image"],
    "virtual image": ["real image", "diminished image", "magnified image", "inverted image", "erect image", "diffused image"],
    "lens formula": ["mirror formula", "Snell’s law", "Ohm’s law", "Newton’s law", "Kirchhoff’s law", "Boyle’s law", "Faraday’s law"],
    "magnification": ["power", "resolution", "refraction", "reflection", "intensity", "luminosity", "spectrum"],
    "ray diagram": ["circuit diagram", "flowchart", "histogram", "graph", "table", "block diagram", "scatter plot"],
    "power of lens": ["focal length", "optical density", "refractive index", "light intensity", "wavelength", "frequency", "transmittance"],
    "accommodation of eye": ["myopia", "hypermetropia", "presbyopia", "astigmatism", "cataract", "glaucoma", "corneal opacity"],
    "myopia": ["hypermetropia", "presbyopia", "astigmatism", "cataract", "glaucoma", "color blindness", "night blindness"],
    "hypermetropia": ["myopia", "presbyopia", "astigmatism", "cataract", "glaucoma", "color blindness", "night blindness"],
    "presbyopia": ["myopia", "hypermetropia", "astigmatism", "cataract", "glaucoma", "color blindness", "night blindness"],
    "astigmatism": ["myopia", "hypermetropia", "presbyopia", "cataract", "glaucoma", "color blindness", "night blindness"],
    "cataract": ["glaucoma", "myopia", "hypermetropia", "presbyopia", "astigmatism", "color blindness", "night blindness"],
    "glaucoma": ["cataract", "myopia", "hypermetropia", "presbyopia", "astigmatism", "color blindness", "night blindness"],
    "convex mirror": ["concave mirror", "concave lens", "convex lens", "plane mirror", "prism", "diffuser", "polarizer"],
    "concave mirror": ["convex mirror", "concave lens", "convex lens", "plane mirror", "prism", "diffuser", "polarizer"],
    "mirror formula": ["lens formula", "Snell’s law", "Ohm’s law", "Newton’s law", "Kirchhoff’s law", "Boyle’s law", "Faraday’s law"],
    "rainbow": ["halo", "mirage", "eclipse", "constellation", "aurora", "glow", "shadow"],
    "total internal reflection": ["diffraction", "dispersion", "polarization", "scattering", "absorption", "interference", "fluorescence"],
    "prism": ["mirror", "lens", "polarizer", "diffuser", "conductor", "capacitor", "resistor"],
    "dispersion": ["refraction", "reflection", "scattering", "diffraction", "absorption", "polarization", "interference"],
    "optical fiber": ["copper wire", "aluminum wire", "semiconductor", "conductor", "dielectric", "inductor", "resistor"],
    "binoculars": ["telescope", "microscope", "periscope", "kaleidoscope", "magnifying glass", "camera", "prism"],
    "telescope": ["microscope", "periscope", "binoculars", "camera", "projector", "laser", "mirror"],
    "microscope": ["telescope", "periscope", "binoculars", "camera", "projector", "laser", "mirror"],
    "spectacles": ["contact lenses", "binoculars", "magnifying glass", "camera lens", "telescope", "microscope", "eye drops"],
    "corrective lens": ["concave mirror", "convex mirror", "polarizer", "prism", "binoculars", "filter", "conductor"],
    "far point": ["near point", "focal point", "optical center", "principal axis", "vertex", "center of curvature", "focus"],
    "near point": ["far point", "focal point", "optical center", "principal axis", "vertex", "center of curvature", "focus"],
    "lensmaker’s formula": ["mirror formula", "lens formula", "power of lens", "Snell’s law", "Ohm’s law", "Kirchhoff’s law", "Boyle’s law"],
    "eye lens": ["cornea", "iris", "retina", "pupil", "optic nerve", "sclera", "ciliary muscles"],
    "cornea": ["lens", "retina", "iris", "pupil", "optic nerve", "sclera", "ciliary muscles"],
    "retina": ["lens", "cornea", "iris", "pupil", "optic nerve", "sclera", "ciliary muscles"],
    "iris": ["lens", "cornea", "retina", "pupil", "optic nerve", "sclera", "ciliary muscles"],
    "pupil": ["lens", "cornea", "retina", "iris", "optic nerve", "sclera", "ciliary muscles"],
    "optic nerve": ["lens", "cornea", "retina", "iris", "pupil", "sclera", "ciliary muscles"],
    #chapter8

    "metallurgy": ["alloying", "electrolysis", "crystallization", "smelting", "roasting", "refining", "corrosion"],
    "mineral": ["ore", "rock", "metal", "crystal", "compound", "isotope", "sediment"],
    "ore": ["mineral", "rock", "metal", "crystal", "alloy", "slag", "sand"],
    "gangue": ["flux", "slag", "ore", "metal", "impurity", "residue", "ash"],
    "flux": ["gangue", "slag", "ore", "catalyst", "reactant", "solvent", "reagent"],
    "slag": ["flux", "gangue", "ore", "ash", "coke", "metal", "residue"],
    "smelting": ["roasting", "calcination", "electrolysis", "refining", "distillation", "oxidation", "fermentation"],
    "roasting": ["smelting", "calcination", "electrolysis", "refining", "oxidation", "fermentation", "sublimation"],
    "calcination": ["roasting", "smelting", "electrolysis", "refining", "oxidation", "filtration", "sublimation"],
    "refining": ["smelting", "roasting", "calcination", "distillation", "filtration", "sedimentation", "sublimation"],
    "alloy": ["metal", "ore", "mineral", "slag", "ceramic", "polymer", "compound"],
    "ferrous metals": ["non-ferrous metals", "alloys", "metalloids", "compounds", "non-metals", "minerals", "ores"],
    "non-ferrous metals": ["ferrous metals", "alloys", "metalloids", "compounds", "non-metals", "minerals", "ores"],
    "oxidation": ["reduction", "ionization", "fermentation", "neutralization", "condensation", "polymerization", "precipitation"],
    "reduction": ["oxidation", "ionization", "fermentation", "neutralization", "condensation", "polymerization", "precipitation"],
    "electrolysis": ["smelting", "roasting", "calcination", "refining", "distillation", "oxidation", "fermentation"],
    "anode": ["cathode", "electrode", "battery", "circuit", "resistor", "conductor", "cell"],
    "cathode": ["anode", "electrode", "battery", "circuit", "resistor", "conductor", "cell"],
    "corrosion": ["rusting", "oxidation", "reduction", "neutralization", "decomposition", "polymerization", "precipitation"],
    "rusting": ["corrosion", "oxidation", "reduction", "neutralization", "decomposition", "polymerization", "precipitation"],
    "galvanization": ["electroplating", "coating", "painting", "rusting", "oxidation", "sublimation", "sedimentation"],
    "electroplating": ["galvanization", "coating", "painting", "rusting", "oxidation", "sublimation", "sedimentation"],
    "anodizing": ["galvanization", "electroplating", "coating", "painting", "oxidation", "sublimation", "neutralization"],
    "pig iron": ["cast iron", "wrought iron", "stainless steel", "alloy steel", "mild steel", "carbon steel", "tool steel"],
    "cast iron": ["pig iron", "wrought iron", "stainless steel", "alloy steel", "mild steel", "carbon steel", "tool steel"],
    "wrought iron": ["pig iron", "cast iron", "stainless steel", "alloy steel", "mild steel", "carbon steel", "tool steel"],
    "stainless steel": ["pig iron", "cast iron", "wrought iron", "alloy steel", "mild steel", "carbon steel", "tool steel"],
    "alloy steel": ["pig iron", "cast iron", "wrought iron", "stainless steel", "mild steel", "carbon steel", "tool steel"],
    "mild steel": ["pig iron", "cast iron", "wrought iron", "stainless steel", "alloy steel", "carbon steel", "tool steel"],
    "carbon steel": ["pig iron", "cast iron", "wrought iron", "stainless steel", "alloy steel", "mild steel", "tool steel"],
    "tool steel": ["pig iron", "cast iron", "wrought iron", "stainless steel", "alloy steel", "mild steel", "carbon steel"],
    "recycling": ["melting", "smelting", "roasting", "calcination", "oxidation", "distillation", "fermentation"],
    "coke": ["charcoal", "carbon", "graphite", "bitumen", "limestone", "slag", "ash"],
    "limestone": ["coke", "charcoal", "carbon", "graphite", "bitumen", "slag", "ash"],
    "blast furnace": ["electric furnace", "induction furnace", "arc furnace", "crucible furnace", "kiln", "converter", "smelter"],
    "Bessemer converter": ["blast furnace", "electric furnace", "induction furnace", "arc furnace", "crucible furnace", "kiln", "smelter"],
    "electric furnace": ["blast furnace", "Bessemer converter", "induction furnace", "arc furnace", "crucible furnace", "kiln", "smelter"],
    "induction furnace": ["blast furnace", "Bessemer converter", "electric furnace", "arc furnace", "crucible furnace", "kiln", "smelter"],
    "arc furnace": ["blast furnace", "Bessemer converter", "electric furnace", "induction furnace", "crucible furnace", "kiln", "smelter"],
    "crucible furnace": ["blast furnace", "Bessemer converter", "electric furnace", "induction furnace", "arc furnace", "kiln", "smelter"],
    "kiln": ["blast furnace", "Bessemer converter", "electric furnace", "induction furnace", "arc furnace", "crucible furnace", "smelter"],
    "smelter": ["blast furnace", "Bessemer converter", "electric furnace", "induction furnace", "arc furnace", "crucible furnace", "kiln"],
    "ductility": ["malleability", "toughness", "hardness", "brittleness", "elasticity", "density", "porosity"],
    "malleability": ["ductility", "toughness", "hardness", "brittleness", "elasticity", "density", "porosity"],
    "hardness": ["ductility", "malleability", "toughness", "brittleness", "elasticity", "density", "porosity"],
    "brittleness": ["ductility", "malleability", "toughness", "hardness", "elasticity", "density", "porosity"],
    "elasticity": ["ductility", "malleability", "toughness", "hardness", "brittleness", "density", "porosity"],
    "density": ["ductility", "malleability", "toughness", "hardness", "brittleness", "elasticity", "porosity"],
    "porosity": ["ductility", "malleability", "toughness", "hardness", "brittleness", "elasticity", "density"],
   #chapter9

    "organic chemistry": ["inorganic chemistry", "biochemistry", "analytical chemistry", "physical chemistry", "thermochemistry", "polymer chemistry", "nuclear chemistry"],
    "hydrocarbon": ["carbohydrate", "lipid", "protein", "enzyme", "polymer", "nucleotide", "vitamin"],
    "alkane": ["alkene", "alkyne", "aromatic compound", "carbohydrate", "ester", "ketone", "amide"],
    "alkene": ["alkane", "alkyne", "aromatic compound", "carbohydrate", "ester", "ketone", "amide"],
    "alkyne": ["alkane", "alkene", "aromatic compound", "carbohydrate", "ester", "ketone", "amide"],
    "saturated hydrocarbon": ["unsaturated hydrocarbon", "alcohol", "aldehyde", "ketone", "ether", "carboxylic acid", "ester"],
    "unsaturated hydrocarbon": ["saturated hydrocarbon", "alcohol", "aldehyde", "ketone", "ether", "carboxylic acid", "ester"],
    "functional group": ["homologous series", "isomer", "radical", "polymer", "monomer", "catalyst", "emulsion"],
    "alcohol": ["aldehyde", "ketone", "carboxylic acid", "ester", "ether", "phenol", "amine"],
    "aldehyde": ["alcohol", "ketone", "carboxylic acid", "ester", "ether", "phenol", "amine"],
    "ketone": ["alcohol", "aldehyde", "carboxylic acid", "ester", "ether", "phenol", "amine"],
    "carboxylic acid": ["alcohol", "aldehyde", "ketone", "ester", "ether", "phenol", "amine"],
    "ester": ["alcohol", "aldehyde", "ketone", "carboxylic acid", "ether", "phenol", "amine"],
    "ether": ["alcohol", "aldehyde", "ketone", "carboxylic acid", "ester", "phenol", "amine"],
    "phenol": ["alcohol", "aldehyde", "ketone", "carboxylic acid", "ester", "ether", "amine"],
    "amine": ["alcohol", "aldehyde", "ketone", "carboxylic acid", "ester", "ether", "phenol"],
    "isomerism": ["polymerization", "sublimation", "fermentation", "electrolysis", "distillation", "neutralization", "oxidation"],
    "homologous series": ["functional group", "isomer", "radical", "polymer", "monomer", "catalyst", "emulsion"],
    "combustion": ["oxidation", "reduction", "neutralization", "saponification", "polymerization", "fermentation", "hydrolysis"],
    "oxidation": ["reduction", "combustion", "neutralization", "saponification", "polymerization", "fermentation", "hydrolysis"],
    "reduction": ["oxidation", "combustion", "neutralization", "saponification", "polymerization", "fermentation", "hydrolysis"],
    "saponification": ["combustion", "oxidation", "reduction", "neutralization", "polymerization", "fermentation", "hydrolysis"],
    "fermentation": ["combustion", "oxidation", "reduction", "neutralization", "saponification", "polymerization", "hydrolysis"],
    "polymerization": ["combustion", "oxidation", "reduction", "neutralization", "saponification", "fermentation", "hydrolysis"],
    "hydrolysis": ["combustion", "oxidation", "reduction", "neutralization", "saponification", "polymerization", "fermentation"],
    "soap": ["detergent", "shampoo", "surfactant", "conditioner", "emulsion", "solvent", "polymer"],
    "detergent": ["soap", "shampoo", "surfactant", "conditioner", "emulsion", "solvent", "polymer"],
    "polymer": ["monomer", "oligomer", "radical", "catalyst", "isomer", "resin", "macromolecule"],
    "monomer": ["polymer", "oligomer", "radical", "catalyst", "isomer", "resin", "macromolecule"],
    "plastic": ["rubber", "glass", "ceramic", "wood", "metal", "fiber", "leather"],
    "nylon": ["polyester", "polyethylene", "polystyrene", "rubber", "Teflon", "Bakelite", "PVC"],
    "polyester": ["nylon", "polyethylene", "polystyrene", "rubber", "Teflon", "Bakelite", "PVC"],
    "polyethylene": ["nylon", "polyester", "polystyrene", "rubber", "Teflon", "Bakelite", "PVC"],
    "polystyrene": ["nylon", "polyester", "polyethylene", "rubber", "Teflon", "Bakelite", "PVC"],
    "Teflon": ["nylon", "polyester", "polyethylene", "polystyrene", "rubber", "Bakelite", "PVC"],
    "Bakelite": ["nylon", "polyester", "polyethylene", "polystyrene", "rubber", "Teflon", "PVC"],
    "PVC": ["nylon", "polyester", "polyethylene", "polystyrene", "rubber", "Teflon", "Bakelite"],
    "biodegradable": ["non-biodegradable", "recyclable", "flammable", "corrosive", "radioactive", "toxic", "hazardous"],
    "non-biodegradable": ["biodegradable", "recyclable", "flammable", "corrosive", "radioactive", "toxic", "hazardous"],
    "recyclable": ["biodegradable", "non-biodegradable", "flammable", "corrosive", "radioactive", "toxic", "hazardous"],
    "flammable": ["biodegradable", "non-biodegradable", "recyclable", "corrosive", "radioactive", "toxic", "hazardous"],
    "corrosive": ["biodegradable", "non-biodegradable", "recyclable", "flammable", "radioactive", "toxic", "hazardous"],
    "radioactive": ["biodegradable", "non-biodegradable", "recyclable", "flammable", "corrosive", "toxic", "hazardous"],
    "toxic": ["biodegradable", "non-biodegradable", "recyclable", "flammable", "corrosive", "radioactive", "hazardous"],
    "hazardous": ["biodegradable", "non-biodegradable", "recyclable", "flammable", "corrosive", "radioactive", "toxic"],
    #chapter10

    "periodic table": ["Mendeleev's table", "modern table", "reactivity series", "electrochemical series", "activity series", "atomic structure", "chemical bonding"],
    "group": ["period", "block", "series", "classification", "trend", "isotope", "ion"],
    "period": ["group", "block", "series", "classification", "trend", "isotope", "ion"],
    "alkali metals": ["alkaline earth metals", "halogens", "noble gases", "transition metals", "lanthanides", "actinides", "metalloids"],
    "alkaline earth metals": ["alkali metals", "halogens", "noble gases", "transition metals", "lanthanides", "actinides", "metalloids"],
    "halogens": ["alkali metals", "alkaline earth metals", "noble gases", "transition metals", "lanthanides", "actinides", "metalloids"],
    "noble gases": ["alkali metals", "alkaline earth metals", "halogens", "transition metals", "lanthanides", "actinides", "metalloids"],
    "transition metals": ["alkali metals", "alkaline earth metals", "halogens", "noble gases", "lanthanides", "actinides", "metalloids"],
    "lanthanides": ["alkali metals", "alkaline earth metals", "halogens", "noble gases", "transition metals", "actinides", "metalloids"],
    "actinides": ["alkali metals", "alkaline earth metals", "halogens", "noble gases", "transition metals", "lanthanides", "metalloids"],
    "metalloids": ["alkali metals", "alkaline earth metals", "halogens", "noble gases", "transition metals", "lanthanides", "actinides"],
    "atomic number": ["atomic mass", "mass number", "isotopes", "ionization energy", "electronegativity", "valency", "oxidation state"],
    "atomic mass": ["atomic number", "mass number", "isotopes", "ionization energy", "electronegativity", "valency", "oxidation state"],
    "mass number": ["atomic number", "atomic mass", "isotopes", "ionization energy", "electronegativity", "valency", "oxidation state"],
    "isotopes": ["isobars", "ions", "elements", "compounds", "molecules", "allotropes", "nucleons"],
    "isobars": ["isotopes", "ions", "elements", "compounds", "molecules", "allotropes", "nucleons"],
    "ionization energy": ["electronegativity", "electron affinity", "valency", "oxidation state", "atomic radius", "melting point", "boiling point"],
    "electronegativity": ["ionization energy", "electron affinity", "valency", "oxidation state", "atomic radius", "melting point", "boiling point"],
    "electron affinity": ["ionization energy", "electronegativity", "valency", "oxidation state", "atomic radius", "melting point", "boiling point"],
    "valency": ["ionization energy", "electronegativity", "electron affinity", "oxidation state", "atomic radius", "melting point", "boiling point"],
    "oxidation state": ["ionization energy", "electronegativity", "electron affinity", "valency", "atomic radius", "melting point", "boiling point"],
    "atomic radius": ["ionization energy", "electronegativity", "electron affinity", "valency", "oxidation state", "melting point", "boiling point"],
    "covalent bond": ["ionic bond", "metallic bond", "hydrogen bond", "dipole-dipole bond", "van der Waals force", "peptide bond", "ester bond"],
    "ionic bond": ["covalent bond", "metallic bond", "hydrogen bond", "dipole-dipole bond", "van der Waals force", "peptide bond", "ester bond"],
    "metallic bond": ["covalent bond", "ionic bond", "hydrogen bond", "dipole-dipole bond", "van der Waals force", "peptide bond", "ester bond"],
    "hydrogen bond": ["covalent bond", "ionic bond", "metallic bond", "dipole-dipole bond", "van der Waals force", "peptide bond", "ester bond"],
    "Mendeleev's periodic law": ["modern periodic law", "Dalton's atomic theory", "Bohr's model", "Einstein's equation", "Newton's law", "Boyle's law", "Avogadro's law"],
    "modern periodic law": ["Mendeleev's periodic law", "Dalton's atomic theory", "Bohr's model", "Einstein's equation", "Newton's law", "Boyle's law", "Avogadro's law"],
    "Dobereiner's triads": ["Newlands' octaves", "Mendeleev's table", "modern table", "law of definite proportions", "law of multiple proportions", "law of conservation of mass", "law of gaseous volumes"],
    "Newlands' octaves": ["Dobereiner's triads", "Mendeleev's table", "modern table", "law of definite proportions", "law of multiple proportions", "law of conservation of mass", "law of gaseous volumes"],
    "periodicity": ["classification", "arrangement", "reactivity", "combination", "sublimation", "extraction", "formation"],
    "metal": ["non-metal", "metalloid", "compound", "alloy", "mixture", "element", "isotope"],
    "non-metal": ["metal", "metalloid", "compound", "alloy", "mixture", "element", "isotope"],
    "alloy": ["metal", "non-metal", "metalloid", "mixture", "compound", "element", "molecule"],
    "radioactivity": ["conductivity", "reactivity", "neutralization", "sublimation", "oxidation", "fermentation", "polymerization"],
    "lanthanide contraction": ["actinide contraction", "electronegativity", "ionization energy", "atomic radius", "oxidation state", "melting point", "boiling point"],
    "actinide contraction": ["lanthanide contraction", "electronegativity", "ionization energy", "atomic radius", "oxidation state", "melting point", "boiling point"],
   #-----------------------------------------------------------------------------------------------SCIENCE2--------------------------------------------------------------------------------------------------

        #chapter1

    "heredity": ["evolution", "mutation", "adaptation", "variation", "genetics", "inheritance", "DNA"],
    "evolution": ["heredity", "mutation", "adaptation", "variation", "genetics", "inheritance", "DNA"],
    "genetics": ["evolution", "mutation", "adaptation", "variation", "heredity", "inheritance", "DNA"],
    "mutation": ["evolution", "genetics", "adaptation", "variation", "heredity", "inheritance", "DNA"],
    "variation": ["mutation", "adaptation", "genetics", "evolution", "heredity", "inheritance", "DNA"],
    "adaptation": ["mutation", "variation", "genetics", "evolution", "heredity", "inheritance", "DNA"],
    "inheritance": ["mutation", "variation", "genetics", "evolution", "heredity", "adaptation", "DNA"],
    "DNA": ["RNA", "protein", "chromosome", "cell", "nucleus", "gene", "allele"],
    "RNA": ["DNA", "protein", "chromosome", "cell", "nucleus", "gene", "allele"],
    "gene": ["allele", "trait", "chromosome", "nucleotide", "gamete", "codon", "genome"],
    "allele": ["gene", "trait", "chromosome", "nucleotide", "gamete", "codon", "genome"],
    "chromosome": ["gene", "allele", "trait", "nucleotide", "gamete", "codon", "genome"],
    "trait": ["gene", "allele", "chromosome", "nucleotide", "gamete", "codon", "genome"],
    "nucleotide": ["gene", "allele", "chromosome", "trait", "gamete", "codon", "genome"],
    "gamete": ["zygote", "sperm", "egg", "fertilization", "embryo", "mutation", "DNA"],
    "zygote": ["gamete", "sperm", "egg", "fertilization", "embryo", "mutation", "DNA"],
    "dominant trait": ["recessive trait", "heterozygous", "homozygous", "phenotype", "genotype", "codominance", "incomplete dominance"],
    "recessive trait": ["dominant trait", "heterozygous", "homozygous", "phenotype", "genotype", "codominance", "incomplete dominance"],
    "phenotype": ["genotype", "dominant trait", "recessive trait", "homozygous", "heterozygous", "allele", "chromosome"],
    "genotype": ["phenotype", "dominant trait", "recessive trait", "homozygous", "heterozygous", "allele", "chromosome"],
    "homozygous": ["heterozygous", "dominant trait", "recessive trait", "phenotype", "genotype", "allele", "chromosome"],
    "heterozygous": ["homozygous", "dominant trait", "recessive trait", "phenotype", "genotype", "allele", "chromosome"],
    "Mendel": ["Darwin", "Lamarck", "Wallace", "Watson", "Crick", "Morgan", "Pasteur"],
    "Darwin": ["Mendel", "Lamarck", "Wallace", "Watson", "Crick", "Morgan", "Pasteur"],
    "Lamarck": ["Mendel", "Darwin", "Wallace", "Watson", "Crick", "Morgan", "Pasteur"],
    "Wallace": ["Mendel", "Darwin", "Lamarck", "Watson", "Crick", "Morgan", "Pasteur"],
    "natural selection": ["artificial selection", "genetic drift", "speciation", "mutation", "variation", "inheritance", "evolution"],
    "artificial selection": ["natural selection", "genetic drift", "speciation", "mutation", "variation", "inheritance", "evolution"],
    "genetic drift": ["natural selection", "artificial selection", "speciation", "mutation", "variation", "inheritance", "evolution"],
    "speciation": ["genetic drift", "natural selection", "artificial selection", "mutation", "variation", "inheritance", "evolution"],
    "extinction": ["adaptation", "natural selection", "mutation", "speciation", "fossilization", "evolution", "genetic drift"],
    "fossilization": ["extinction", "natural selection", "mutation", "speciation", "adaptation", "evolution", "genetic drift"],
    "homologous structures": ["analogous structures", "vestigial structures", "fossil evidence", "genetic evidence", "embryological evidence", "biogeography", "phylogenetics"],
    "analogous structures": ["homologous structures", "vestigial structures", "fossil evidence", "genetic evidence", "embryological evidence", "biogeography", "phylogenetics"],
    "vestigial structures": ["homologous structures", "analogous structures", "fossil evidence", "genetic evidence", "embryological evidence", "biogeography", "phylogenetics"],
    "fossil evidence": ["homologous structures", "analogous structures", "vestigial structures", "genetic evidence", "embryological evidence", "biogeography", "phylogenetics"],
    "genetic evidence": ["homologous structures", "analogous structures", "vestigial structures", "fossil evidence", "embryological evidence", "biogeography", "phylogenetics"],
    "embryological evidence": ["homologous structures", "analogous structures", "vestigial structures", "fossil evidence", "genetic evidence", "biogeography", "phylogenetics"],
    "biogeography": ["homologous structures", "analogous structures", "vestigial structures", "fossil evidence", "genetic evidence", "embryological evidence", "phylogenetics"],
    "phylogenetics": ["homologous structures", "analogous structures", "vestigial structures", "fossil evidence", "genetic evidence", "embryological evidence", "biogeography"],
    "adaptive radiation": ["convergent evolution", "divergent evolution", "speciation", "mutation", "genetic drift", "natural selection", "inheritance"],
    "convergent evolution": ["adaptive radiation", "divergent evolution", "speciation", "mutation", "genetic drift", "natural selection", "inheritance"],
    "divergent evolution": ["adaptive radiation", "convergent evolution", "speciation", "mutation", "genetic drift", "natural selection", "inheritance"],
    "human evolution": ["natural selection", "genetic drift", "speciation", "mutation", "variation", "inheritance", "artificial selection"],
    "paleontology": ["genetics", "evolution", "heredity", "variation", "mutation", "natural selection", "taxonomy"],
        #chapter2

    "cell": ["tissue", "organ", "nucleus", "mitochondria", "ribosome", "chloroplast", "membrane"],
    "mitochondria": ["chloroplast", "nucleus", "ribosome", "endoplasmic reticulum", "Golgi apparatus", "lysosome", "peroxisome"],
    "chloroplast": ["mitochondria", "nucleus", "ribosome", "endoplasmic reticulum", "Golgi apparatus", "lysosome", "peroxisome"],
    "nucleus": ["mitochondria", "chloroplast", "ribosome", "endoplasmic reticulum", "Golgi apparatus", "lysosome", "peroxisome"],
    "ribosome": ["nucleus", "mitochondria", "chloroplast", "endoplasmic reticulum", "Golgi apparatus", "lysosome", "peroxisome"],
    "endoplasmic reticulum": ["ribosome", "nucleus", "mitochondria", "chloroplast", "Golgi apparatus", "lysosome", "peroxisome"],
    "Golgi apparatus": ["ribosome", "nucleus", "mitochondria", "chloroplast", "endoplasmic reticulum", "lysosome", "peroxisome"],
    "lysosome": ["ribosome", "nucleus", "mitochondria", "chloroplast", "endoplasmic reticulum", "Golgi apparatus", "peroxisome"],
    "diffusion": ["osmosis", "active transport", "passive transport", "facilitated diffusion", "endocytosis", "exocytosis", "phagocytosis"],
    "osmosis": ["diffusion", "active transport", "passive transport", "facilitated diffusion", "endocytosis", "exocytosis", "phagocytosis"],
    "active transport": ["diffusion", "osmosis", "passive transport", "facilitated diffusion", "endocytosis", "exocytosis", "phagocytosis"],
    "passive transport": ["diffusion", "osmosis", "active transport", "facilitated diffusion", "endocytosis", "exocytosis", "phagocytosis"],
    "facilitated diffusion": ["diffusion", "osmosis", "active transport", "passive transport", "endocytosis", "exocytosis", "phagocytosis"],
    "endocytosis": ["exocytosis", "diffusion", "osmosis", "active transport", "passive transport", "facilitated diffusion", "phagocytosis"],
    "exocytosis": ["endocytosis", "diffusion", "osmosis", "active transport", "passive transport", "facilitated diffusion", "phagocytosis"],
    "phagocytosis": ["pinocytosis", "diffusion", "osmosis", "active transport", "passive transport", "facilitated diffusion", "endocytosis"],
    "pinocytosis": ["phagocytosis", "diffusion", "osmosis", "active transport", "passive transport", "facilitated diffusion", "endocytosis"],
    "photosynthesis": ["respiration", "fermentation", "glycolysis", "Krebs cycle", "electron transport chain", "transpiration", "chlorophyll"],
    "respiration": ["photosynthesis", "fermentation", "glycolysis", "Krebs cycle", "electron transport chain", "transpiration", "chlorophyll"],
    "glycolysis": ["Krebs cycle", "electron transport chain", "respiration", "fermentation", "photosynthesis", "oxidation", "ATP synthesis"],
    "Krebs cycle": ["glycolysis", "electron transport chain", "respiration", "fermentation", "photosynthesis", "oxidation", "ATP synthesis"],
    "electron transport chain": ["glycolysis", "Krebs cycle", "respiration", "fermentation", "photosynthesis", "oxidation", "ATP synthesis"],
    "fermentation": ["glycolysis", "Krebs cycle", "respiration", "photosynthesis", "oxidation", "transpiration", "ATP synthesis"],
    "ATP": ["ADP", "glucose", "NADH", "FADH2", "pyruvate", "ribose", "phosphate"],
    "ADP": ["ATP", "glucose", "NADH", "FADH2", "pyruvate", "ribose", "phosphate"],
    "NADH": ["FADH2", "ATP", "ADP", "glucose", "pyruvate", "ribose", "phosphate"],
    "FADH2": ["NADH", "ATP", "ADP", "glucose", "pyruvate", "ribose", "phosphate"],
    "pyruvate": ["glucose", "ATP", "ADP", "NADH", "FADH2", "ribose", "phosphate"],
    "glucose": ["pyruvate", "ATP", "ADP", "NADH", "FADH2", "ribose", "phosphate"],
    "ribose": ["phosphate", "ATP", "ADP", "NADH", "FADH2", "pyruvate", "glucose"],
    "phosphate": ["ribose", "ATP", "ADP", "NADH", "FADH2", "pyruvate", "glucose"],
    "stomata": ["chloroplast", "xylem", "phloem", "epidermis", "cuticle", "guard cells", "mesophyll"],
    "xylem": ["phloem", "stomata", "chloroplast", "epidermis", "cuticle", "guard cells", "mesophyll"],
    "phloem": ["xylem", "stomata", "chloroplast", "epidermis", "cuticle", "guard cells", "mesophyll"],
    "guard cells": ["stomata", "xylem", "phloem", "epidermis", "cuticle", "chloroplast", "mesophyll"],
    "mesophyll": ["stomata", "xylem", "phloem", "epidermis", "cuticle", "guard cells", "chloroplast"],
    "cuticle": ["stomata", "xylem", "phloem", "epidermis", "guard cells", "chloroplast", "mesophyll"],
    "epidermis": ["stomata", "xylem", "phloem", "cuticle", "guard cells", "chloroplast", "mesophyll"],
    "root pressure": ["transpiration", "capillary action", "cohesion", "adhesion", "osmosis", "diffusion", "turgor pressure"],
    "transpiration": ["root pressure", "capillary action", "cohesion", "adhesion", "osmosis", "diffusion", "turgor pressure"],
    "capillary action": ["transpiration", "root pressure", "cohesion", "adhesion", "osmosis", "diffusion", "turgor pressure"],
    "cohesion": ["transpiration", "root pressure", "capillary action", "adhesion", "osmosis", "diffusion", "turgor pressure"],
    "adhesion": ["transpiration", "root pressure", "capillary action", "cohesion", "osmosis", "diffusion", "turgor pressure"],
        #chapter3

    "asexual reproduction": ["sexual reproduction", "binary fission", "budding", "fragmentation", "regeneration", "spore formation", "vegetative propagation"],
    "sexual reproduction": ["asexual reproduction", "binary fission", "budding", "fragmentation", "regeneration", "spore formation", "vegetative propagation"],
    "binary fission": ["budding", "fragmentation", "regeneration", "spore formation", "vegetative propagation", "mitosis", "meiosis"],
    "budding": ["binary fission", "fragmentation", "regeneration", "spore formation", "vegetative propagation", "mitosis", "meiosis"],
    "fragmentation": ["binary fission", "budding", "regeneration", "spore formation", "vegetative propagation", "mitosis", "meiosis"],
    "regeneration": ["binary fission", "budding", "fragmentation", "spore formation", "vegetative propagation", "mitosis", "meiosis"],
    "spore formation": ["binary fission", "budding", "fragmentation", "regeneration", "vegetative propagation", "mitosis", "meiosis"],
    "vegetative propagation": ["binary fission", "budding", "fragmentation", "regeneration", "spore formation", "mitosis", "meiosis"],
    "mitosis": ["meiosis", "binary fission", "budding", "fragmentation", "regeneration", "spore formation", "vegetative propagation"],
    "meiosis": ["mitosis", "binary fission", "budding", "fragmentation", "regeneration", "spore formation", "vegetative propagation"],
    "gamete": ["zygote", "sperm", "egg", "embryo", "ovum", "blastocyst", "haploid"],
    "zygote": ["gamete", "sperm", "egg", "embryo", "ovum", "blastocyst", "haploid"],
    "sperm": ["egg", "zygote", "gamete", "embryo", "ovum", "blastocyst", "haploid"],
    "egg": ["sperm", "zygote", "gamete", "embryo", "ovum", "blastocyst", "haploid"],
    "ovum": ["sperm", "zygote", "gamete", "embryo", "egg", "blastocyst", "haploid"],
    "haploid": ["diploid", "sperm", "zygote", "gamete", "embryo", "egg", "blastocyst"],
    "diploid": ["haploid", "sperm", "zygote", "gamete", "embryo", "egg", "blastocyst"],
    "fertilization": ["ovulation", "implantation", "gestation", "conception", "zygote formation", "blastulation", "gastrulation"],
    "ovulation": ["fertilization", "implantation", "gestation", "conception", "zygote formation", "blastulation", "gastrulation"],
    "implantation": ["fertilization", "ovulation", "gestation", "conception", "zygote formation", "blastulation", "gastrulation"],
    "gestation": ["fertilization", "ovulation", "implantation", "conception", "zygote formation", "blastulation", "gastrulation"],
    "conception": ["fertilization", "ovulation", "implantation", "gestation", "zygote formation", "blastulation", "gastrulation"],
    "blastulation": ["gastrulation", "fertilization", "ovulation", "implantation", "gestation", "conception", "zygote formation"],
    "gastrulation": ["blastulation", "fertilization", "ovulation", "implantation", "gestation", "conception", "zygote formation"],
    "placenta": ["umbilical cord", "amniotic sac", "uterus", "ovary", "fallopian tube", "chorion", "endometrium"],
    "umbilical cord": ["placenta", "amniotic sac", "uterus", "ovary", "fallopian tube", "chorion", "endometrium"],
    "amniotic sac": ["placenta", "umbilical cord", "uterus", "ovary", "fallopian tube", "chorion", "endometrium"],
    "uterus": ["placenta", "umbilical cord", "amniotic sac", "ovary", "fallopian tube", "chorion", "endometrium"],
    "ovary": ["placenta", "umbilical cord", "amniotic sac", "uterus", "fallopian tube", "chorion", "endometrium"],
    "fallopian tube": ["placenta", "umbilical cord", "amniotic sac", "uterus", "ovary", "chorion", "endometrium"],
    "chorion": ["placenta", "umbilical cord", "amniotic sac", "uterus", "ovary", "fallopian tube", "endometrium"],
    "endometrium": ["placenta", "umbilical cord", "amniotic sac", "uterus", "ovary", "fallopian tube", "chorion"],
    "testis": ["ovary", "scrotum", "penis", "vas deferens", "prostate", "epididymis", "urethra"],
    "scrotum": ["testis", "ovary", "penis", "vas deferens", "prostate", "epididymis", "urethra"],
    "penis": ["testis", "ovary", "scrotum", "vas deferens", "prostate", "epididymis", "urethra"],
    "vas deferens": ["testis", "ovary", "scrotum", "penis", "prostate", "epididymis", "urethra"],
    "prostate": ["testis", "ovary", "scrotum", "penis", "vas deferens", "epididymis", "urethra"],
    "epididymis": ["testis", "ovary", "scrotum", "penis", "vas deferens", "prostate", "urethra"],
    "urethra": ["testis", "ovary", "scrotum", "penis", "vas deferens", "prostate", "epididymis"],
    "hormone": ["enzyme", "protein", "lipid", "carbohydrate", "vitamin", "mineral", "nucleotide"],
    "enzyme": ["hormone", "protein", "lipid", "carbohydrate", "vitamin", "mineral", "nucleotide"],
    "protein": ["hormone", "enzyme", "lipid", "carbohydrate", "vitamin", "mineral", "nucleotide"],
    "lipid": ["hormone", "enzyme", "protein", "carbohydrate", "vitamin", "mineral", "nucleotide"],
    "carbohydrate": ["hormone", "enzyme", "protein", "lipid", "vitamin", "mineral", "nucleotide"],
    "vitamin": ["hormone", "enzyme", "protein", "lipid", "carbohydrate", "mineral", "nucleotide"],
    "mineral": ["hormone", "enzyme", "protein", "lipid", "carbohydrate", "vitamin", "nucleotide"],
    #chapter4

    "ecosystem": ["biodiversity", "environment", "community", "habitat", "biosphere", "biome", "food chain"],
    "biodiversity": ["ecosystem", "species", "genetic diversity", "conservation", "sustainability", "climate change", "pollution"],
    "environment": ["climate", "weather", "habitat", "biosphere", "pollution", "sustainability", "ecology"],
    "habitat": ["niche", "ecosystem", "population", "community", "biome", "biosphere", "food web"],
    "biosphere": ["atmosphere", "lithosphere", "hydrosphere", "stratosphere", "ecosystem", "biome", "trophic level"],
    "food chain": ["food web", "energy pyramid", "trophic level", "decomposer", "herbivore", "omnivore", "producer"],
    "food web": ["food chain", "energy pyramid", "trophic level", "decomposer", "carnivore", "omnivore", "ecosystem"],
    "sustainability": ["conservation", "pollution", "global warming", "climate change", "carbon footprint", "renewable energy", "biodiversity"],
    "climate change": ["global warming", "ozone depletion", "greenhouse gases", "acid rain", "pollution", "carbon footprint", "deforestation"],
    "pollution": ["air pollution", "water pollution", "soil pollution", "noise pollution", "radioactive pollution", "plastic waste", "eutrophication"],
    "air pollution": ["water pollution", "soil pollution", "noise pollution", "radioactive pollution", "smog", "acid rain", "carbon monoxide"],
    "water pollution": ["air pollution", "soil pollution", "noise pollution", "radioactive pollution", "eutrophication", "sewage", "oil spill"],
    "soil pollution": ["air pollution", "water pollution", "noise pollution", "radioactive pollution", "pesticides", "deforestation", "waste management"],
    "noise pollution": ["air pollution", "water pollution", "soil pollution", "radioactive pollution", "urbanization", "industrialization", "traffic"],
    "greenhouse effect": ["global warming", "climate change", "ozone depletion", "carbon dioxide", "methane", "water vapor", "fossil fuels"],
    "ozone depletion": ["greenhouse effect", "global warming", "climate change", "CFCs", "ultraviolet rays", "atmosphere", "smog"],
    "deforestation": ["reforestation", "afforestation", "desertification", "soil erosion", "biodiversity loss", "wildlife extinction", "habitat destruction"],
    "reforestation": ["deforestation", "afforestation", "desertification", "forest conservation", "carbon sequestration", "tree plantation", "biodiversity"],
    "afforestation": ["reforestation", "deforestation", "forest degradation", "carbon sink", "ecosystem restoration", "desertification", "carbon capture"],
    "wildlife conservation": ["forest conservation", "biodiversity conservation", "species protection", "national parks", "endangered species", "habitat protection", "sanctuary"],
    "endangered species": ["threatened species", "extinct species", "rare species", "keystone species", "invasive species", "biodiversity loss", "poaching"],
    "invasive species": ["native species", "keystone species", "endangered species", "habitat destruction", "biodiversity loss", "competition", "predation"],
    "carbon footprint": ["ecological footprint", "greenhouse gases", "sustainability", "pollution", "climate change", "global warming", "energy consumption"],
    "renewable energy": ["non-renewable energy", "fossil fuels", "solar energy", "wind energy", "hydroelectric power", "geothermal energy", "biofuel"],
    "non-renewable energy": ["renewable energy", "fossil fuels", "nuclear energy", "coal", "petroleum", "natural gas", "carbon emissions"],
    "fossil fuels": ["coal", "petroleum", "natural gas", "biofuel", "renewable energy", "carbon dioxide", "global warming"],
    "biofuel": ["biodiesel", "ethanol", "solar energy", "wind energy", "hydropower", "geothermal energy", "renewable resource"],
    "hydropower": ["solar power", "wind energy", "geothermal energy", "biofuel", "tidal energy", "nuclear power", "wave energy"],
    "waste management": ["recycling", "composting", "landfill", "incineration", "e-waste", "biodegradable waste", "hazardous waste"],
    "recycling": ["waste management", "composting", "reuse", "biodegradable waste", "plastic waste", "e-waste", "zero waste"],
    "composting": ["recycling", "biodegradable waste", "organic farming", "vermicomposting", "waste management", "landfill", "fertilizer"],
    "e-waste": ["electronic waste", "hazardous waste", "toxic waste", "landfill", "recycling", "pollution", "waste management"],
    "sustainable development": ["economic development", "ecological balance", "biodiversity conservation", "resource management", "green technology", "renewable energy", "carbon neutrality"],
    "carbon neutrality": ["carbon offset", "carbon sequestration", "greenhouse gases", "climate change", "fossil fuel reduction", "sustainability", "renewable energy"],
    "ecological balance": ["ecosystem stability", "biodiversity", "food chain", "trophic level", "environmental equilibrium", "population control", "habitat preservation"],
    "trophic level": ["food chain", "food web", "primary consumer", "secondary consumer", "tertiary consumer", "producer", "decomposer"],
    "decomposer": ["scavenger", "detritivore", "bacteria", "fungi", "microorganisms", "nutrient cycle", "soil fertility"],
    "primary consumer": ["secondary consumer", "tertiary consumer", "herbivore", "omnivore", "producer", "decomposer", "food chain"],
    "secondary consumer": ["primary consumer", "tertiary consumer", "herbivore", "omnivore", "producer", "decomposer", "food web"],
    "tertiary consumer": ["primary consumer", "secondary consumer", "apex predator", "carnivore", "herbivore", "omnivore", "food web"],
    "apex predator": ["tertiary consumer", "secondary consumer", "keystone species", "top predator", "carnivore", "scavenger", "predation"],
    "resource conservation": ["sustainability", "biodiversity conservation", "waste management", "energy conservation", "water conservation", "natural resources", "ecological footprint"],
    #chapter5

    "energy": ["power", "force", "motion", "work", "electricity", "fuel", "current"],
    "renewable energy": ["non-renewable energy", "fossil fuels", "solar energy", "wind energy", "hydroelectric power", "geothermal energy", "biofuel"],
    "non-renewable energy": ["renewable energy", "fossil fuels", "nuclear energy", "coal", "petroleum", "natural gas", "carbon emissions"],
    "fossil fuels": ["coal", "petroleum", "natural gas", "biofuel", "renewable energy", "carbon dioxide", "global warming"],
    "solar energy": ["wind energy", "hydropower", "geothermal energy", "tidal energy", "biomass energy", "nuclear energy", "fossil fuels"],
    "wind energy": ["solar energy", "hydropower", "tidal energy", "geothermal energy", "nuclear energy", "biomass energy", "fossil fuels"],
    "hydropower": ["solar power", "wind energy", "geothermal energy", "biofuel", "tidal energy", "nuclear power", "wave energy"],
    "geothermal energy": ["solar power", "wind energy", "hydropower", "tidal energy", "biomass energy", "nuclear energy", "thermal power"],
    "tidal energy": ["solar energy", "wind energy", "hydropower", "geothermal energy", "nuclear energy", "wave energy", "biomass energy"],
    "biomass energy": ["solar energy", "wind energy", "hydropower", "tidal energy", "nuclear energy", "fossil fuels", "natural gas"],
    "nuclear energy": ["solar energy", "wind energy", "hydropower", "tidal energy", "biomass energy", "radioactive energy", "thermal energy"],
    "biofuel": ["biodiesel", "ethanol", "solar energy", "wind energy", "hydropower", "geothermal energy", "renewable resource"],
    "power plant": ["thermal plant", "nuclear reactor", "hydroelectric dam", "solar farm", "wind farm", "energy grid", "biomass station"],
    "thermal power": ["solar power", "wind energy", "hydropower", "tidal energy", "nuclear energy", "wave energy", "fossil fuel"],
    "coal power": ["solar power", "wind energy", "hydropower", "nuclear power", "geothermal energy", "tidal energy", "biomass energy"],
    "nuclear reactor": ["nuclear fusion", "nuclear fission", "radioactive decay", "power plant", "electric generator", "cooling tower", "reactor core"],
    "radioactive decay": ["nuclear fission", "nuclear fusion", "radiation", "half-life", "isotope", "alpha particles", "gamma rays"],
    "nuclear fission": ["nuclear fusion", "radioactive decay", "chain reaction", "neutron absorption", "critical mass", "reactor core", "coolant"],
    "nuclear fusion": ["nuclear fission", "radioactive decay", "hydrogen bomb", "plasma reaction", "tokamak", "deuterium", "helium"],
    "greenhouse effect": ["global warming", "climate change", "ozone depletion", "carbon dioxide", "methane", "water vapor", "fossil fuels"],
    "carbon footprint": ["ecological footprint", "greenhouse gases", "sustainability", "pollution", "climate change", "global warming", "energy consumption"],
    "global warming": ["climate change", "greenhouse effect", "ozone depletion", "deforestation", "carbon dioxide", "methane", "fossil fuels"],
    "climate change": ["global warming", "ozone depletion", "greenhouse gases", "acid rain", "pollution", "carbon footprint", "deforestation"],
    "ozone depletion": ["greenhouse effect", "global warming", "climate change", "CFCs", "ultraviolet rays", "atmosphere", "smog"],
    "carbon sequestration": ["carbon offset", "carbon capture", "greenhouse gas reduction", "sustainability", "tree plantation", "carbon sink", "reforestation"],
    "carbon offset": ["carbon neutrality", "carbon sequestration", "renewable energy", "fossil fuel reduction", "climate action", "sustainability", "green energy"],
    "energy conservation": ["power saving", "efficiency", "smart grid", "sustainable use", "low energy appliances", "reduced consumption", "green building"],
    "energy efficiency": ["energy conservation", "power saving", "smart grid", "sustainable technology", "low carbon emission", "green industry", "solar panels"],
    "electric vehicle": ["hybrid vehicle", "fuel cell car", "solar car", "hydrogen vehicle", "EV charging station", "eco-friendly transport", "battery technology"],
    "smart grid": ["electricity grid", "power transmission", "energy management", "load balancing", "renewable integration", "efficiency", "sustainable energy"],
    "battery storage": ["lithium-ion battery", "solar battery", "energy storage", "power backup", "grid stability", "electric vehicle", "charge retention"],
    "fuel cell": ["hydrogen cell", "battery storage", "solar cell", "biofuel cell", "energy conversion", "electrochemical reaction", "power generation"],
    "hydrogen fuel": ["fuel cell", "electric vehicle", "renewable gas", "zero-emission fuel", "energy carrier", "green hydrogen", "hydrogen economy"],
    "wave energy": ["tidal energy", "hydropower", "wind energy", "solar energy", "ocean currents", "marine power", "offshore energy"],
    "solar panel": ["photovoltaic cell", "solar collector", "energy converter", "renewable technology", "power generator", "green energy", "eco-friendly"],
    "photovoltaic cell": ["solar panel", "light energy conversion", "semi-conductor", "electricity generation", "photonic energy", "charge separation", "solar technology"],
    "energy grid": ["power transmission", "smart grid", "electric network", "distribution system", "voltage regulation", "renewable integration", "electric power"],
    "hydrogen economy": ["green hydrogen", "fuel cell technology", "zero-carbon energy", "hydrogen fuel", "alternative energy", "sustainable economy", "energy transition"],
    "zero-emission": ["carbon neutral", "clean energy", "renewable technology", "sustainable development", "eco-friendly transport", "low-carbon economy", "green technology"],
    "clean energy": ["renewable energy", "sustainable energy", "carbon-free power", "green technology", "low-emission power", "alternative fuels", "environment-friendly"],
        #chapter6

    "vertebrates": ["invertebrates", "arthropods", "mollusks", "annelids", "cnidarians", "echinoderms", "porifera"],
    "invertebrates": ["vertebrates", "chordates", "mammals", "reptiles", "amphibians", "birds", "fishes"],
    "chordates": ["non-chordates", "mollusks", "arthropods", "echinoderms", "annelids", "sponges", "cnidarians"],
    "mammals": ["reptiles", "amphibians", "birds", "fishes", "arthropods", "mollusks", "cnidarians"],
    "reptiles": ["amphibians", "birds", "mammals", "fishes", "insects", "arthropods", "echinoderms"],
    "amphibians": ["reptiles", "mammals", "birds", "fishes", "arthropods", "annelids", "mollusks"],
    "birds": ["mammals", "reptiles", "amphibians", "fishes", "arthropods", "mollusks", "sponges"],
    "fishes": ["mammals", "reptiles", "amphibians", "birds", "arthropods", "cnidarians", "echinoderms"],
    "arthropods": ["annelids", "mollusks", "echinoderms", "cnidarians", "sponges", "nematodes", "chordates"],
    "annelids": ["arthropods", "mollusks", "echinoderms", "cnidarians", "sponges", "platyhelminthes", "nematodes"],
    "mollusks": ["arthropods", "annelids", "echinoderms", "cnidarians", "sponges", "platyhelminthes", "nematodes"],
    "cnidarians": ["mollusks", "arthropods", "annelids", "echinoderms", "sponges", "platyhelminthes", "nematodes"],
    "echinoderms": ["arthropods", "annelids", "mollusks", "cnidarians", "sponges", "platyhelminthes", "nematodes"],
    "porifera": ["arthropods", "annelids", "mollusks", "cnidarians", "echinoderms", "platyhelminthes", "nematodes"],
    "platyhelminthes": ["nematodes", "arthropods", "annelids", "mollusks", "cnidarians", "echinoderms", "sponges"],
    "nematodes": ["platyhelminthes", "arthropods", "annelids", "mollusks", "cnidarians", "echinoderms", "sponges"],
    "bilateral symmetry": ["radial symmetry", "asymmetry", "cephalization", "segmentation", "metamerism", "exoskeleton", "endoskeleton"],
    "radial symmetry": ["bilateral symmetry", "asymmetry", "cephalization", "segmentation", "metamerism", "exoskeleton", "endoskeleton"],
    "asymmetry": ["bilateral symmetry", "radial symmetry", "cephalization", "segmentation", "metamerism", "exoskeleton", "endoskeleton"],
    "exoskeleton": ["endoskeleton", "hydrostatic skeleton", "cartilage", "bone", "segmentation", "metamerism", "molt"],
    "endoskeleton": ["exoskeleton", "hydrostatic skeleton", "cartilage", "bone", "segmentation", "metamerism", "molt"],
    "metamerism": ["segmentation", "exoskeleton", "endoskeleton", "cephalization", "bilateral symmetry", "radial symmetry", "asymmetry"],
    "cephalization": ["segmentation", "metamerism", "bilateral symmetry", "radial symmetry", "asymmetry", "exoskeleton", "endoskeleton"],
    "segmentation": ["metamerism", "cephalization", "bilateral symmetry", "radial symmetry", "asymmetry", "exoskeleton", "endoskeleton"],
    "oviparous": ["viviparous", "asexual reproduction", "budding", "parthenogenesis", "binary fission", "hermaphroditism", "external fertilization"],
    "viviparous": ["oviparous", "asexual reproduction", "budding", "parthenogenesis", "binary fission", "hermaphroditism", "internal fertilization"],
    "hermaphroditism": ["asexual reproduction", "binary fission", "parthenogenesis", "sexual dimorphism", "external fertilization", "viviparity", "oviparity"],
    "parthenogenesis": ["hermaphroditism", "binary fission", "asexual reproduction", "external fertilization", "internal fertilization", "viviparity", "oviparity"],
    "binary fission": ["budding", "hermaphroditism", "parthenogenesis", "external fertilization", "internal fertilization", "viviparity", "oviparity"],
    "external fertilization": ["internal fertilization", "viviparity", "oviparity", "binary fission", "parthenogenesis", "hermaphroditism", "asexual reproduction"],
    "internal fertilization": ["external fertilization", "viviparity", "oviparity", "binary fission", "parthenogenesis", "hermaphroditism", "asexual reproduction"],
    "warm-blooded": ["cold-blooded", "ectothermic", "poikilothermic", "homeothermic", "metabolic heat", "thermoregulation", "insulation"],
    "cold-blooded": ["warm-blooded", "homeothermic", "metabolic heat", "thermoregulation", "insulation", "ectothermic", "poikilothermic"],
    "ectothermic": ["endothermic", "homeothermic", "poikilothermic", "metabolic heat", "thermoregulation", "insulation", "cold-blooded"],
    "endothermic": ["ectothermic", "poikilothermic", "homeothermic", "metabolic heat", "thermoregulation", "insulation", "warm-blooded"],
    "poikilothermic": ["homeothermic", "metabolic heat", "thermoregulation", "insulation", "ectothermic", "cold-blooded", "warm-blooded"],
    "homeothermic": ["poikilothermic", "metabolic heat", "thermoregulation", "insulation", "ectothermic", "cold-blooded", "warm-blooded"],
    "camouflage": ["mimicry", "adaptation", "protective coloration", "cryptic coloration", "disruptive coloration", "countershading", "warning coloration"],
    "mimicry": ["camouflage", "cryptic coloration", "disruptive coloration", "countershading", "warning coloration", "adaptation", "protective coloration"],
    "adaptation": ["evolution", "natural selection", "mutation", "genetic drift", "species variation", "camouflage", "mimicry"],
        #chapter7

    "microbiology": ["biotechnology", "biochemistry", "genetics", "pathology", "immunology", "botany", "zoology"],
    "microorganisms": ["bacteria", "viruses", "fungi", "protozoa", "algae", "prions", "helminths"],
    "bacteria": ["viruses", "fungi", "protozoa", "algae", "prions", "helminths", "archaea"],
    "viruses": ["bacteria", "fungi", "protozoa", "algae", "prions", "helminths", "archaea"],
    "fungi": ["bacteria", "viruses", "protozoa", "algae", "prions", "helminths", "archaea"],
    "protozoa": ["bacteria", "viruses", "fungi", "algae", "prions", "helminths", "archaea"],
    "algae": ["bacteria", "viruses", "fungi", "protozoa", "prions", "helminths", "archaea"],
    "pathogens": ["probiotics", "antibiotics", "enzymes", "immunity", "antigens", "vaccines", "antibodies"],
    "antibiotics": ["probiotics", "antibodies", "vaccines", "enzymes", "hormones", "pathogens", "bacteria"],
    "vaccines": ["antibodies", "antibiotics", "hormones", "enzymes", "pathogens", "probiotics", "mutation"],
    "antibodies": ["vaccines", "antibiotics", "enzymes", "hormones", "pathogens", "immunity", "antigens"],
    "probiotics": ["antibiotics", "antibodies", "vaccines", "enzymes", "hormones", "pathogens", "mutation"],
    "enzymes": ["hormones", "proteins", "lipids", "carbohydrates", "pathogens", "antibodies", "antibiotics"],
    "hormones": ["enzymes", "proteins", "lipids", "carbohydrates", "pathogens", "antibodies", "antibiotics"],
    "fermentation": ["pasteurization", "sterilization", "antiseptic", "vaccination", "mutation", "biotechnology", "preservation"],
    "pasteurization": ["fermentation", "sterilization", "antiseptic", "vaccination", "mutation", "biotechnology", "preservation"],
    "sterilization": ["pasteurization", "fermentation", "antiseptic", "vaccination", "mutation", "biotechnology", "preservation"],
    "antiseptic": ["disinfectant", "antibiotic", "vaccine", "pathogen", "mutation", "biotechnology", "fermentation"],
    "disinfectant": ["antiseptic", "antibiotic", "vaccine", "pathogen", "mutation", "biotechnology", "fermentation"],
    "biotechnology": ["genetic engineering", "microbiology", "biochemistry", "pharmacology", "nanotechnology", "virology", "immunology"],
    "genetic engineering": ["biotechnology", "microbiology", "biochemistry", "pharmacology", "nanotechnology", "virology", "immunology"],
    "mutation": ["variation", "evolution", "adaptation", "natural selection", "artificial selection", "biotechnology", "genetics"],
    "natural selection": ["artificial selection", "mutation", "adaptation", "evolution", "genetics", "biotechnology", "variation"],
    "adaptation": ["evolution", "natural selection", "mutation", "variation", "biotechnology", "genetics", "resistance"],
    "resistance": ["immunity", "mutation", "antibodies", "vaccines", "antibiotics", "probiotics", "infection"],
    "infection": ["pathogen", "disease", "antibodies", "antibiotics", "probiotics", "mutation", "vaccines"],
    "disease": ["infection", "pathogen", "antibodies", "antibiotics", "probiotics", "mutation", "vaccines"],
    "immunity": ["antibodies", "vaccines", "antibiotics", "probiotics", "mutation", "infection", "disease"],
    "antigen": ["antibody", "vaccine", "pathogen", "infection", "disease", "antibiotic", "mutation"],
    "bioremediation": ["fermentation", "biodegradation", "recycling", "genetic engineering", "biotechnology", "mutation", "pollution"],
    "biodegradation": ["bioremediation", "recycling", "fermentation", "genetic engineering", "biotechnology", "mutation", "pollution"],
    "aerobic bacteria": ["anaerobic bacteria", "facultative bacteria", "obligate anaerobes", "pathogens", "microorganisms", "archaea", "fungi"],
    "anaerobic bacteria": ["aerobic bacteria", "facultative bacteria", "obligate aerobes", "pathogens", "microorganisms", "archaea", "fungi"],
    "facultative bacteria": ["aerobic bacteria", "anaerobic bacteria", "obligate aerobes", "pathogens", "microorganisms", "archaea", "fungi"],
    "obligate aerobes": ["aerobic bacteria", "anaerobic bacteria", "facultative bacteria", "pathogens", "microorganisms", "archaea", "fungi"],
    "obligate anaerobes": ["aerobic bacteria", "anaerobic bacteria", "facultative bacteria", "pathogens", "microorganisms", "archaea", "fungi"],
    "industrial microbiology": ["biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation", "microbiology", "pharmacology"],
    "pharmaceutical microbiology": ["biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation", "microbiology", "pharmacology"],
    "food microbiology": ["industrial microbiology", "biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation", "microbiology"],
    "water microbiology": ["food microbiology", "industrial microbiology", "biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation"],
    "agricultural microbiology": ["food microbiology", "industrial microbiology", "biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation"],
    "medical microbiology": ["pharmaceutical microbiology", "food microbiology", "industrial microbiology", "biotechnology", "biochemistry", "genetic engineering", "fermentation"],
    "environmental microbiology": ["bioremediation", "biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation", "microbiology"],
    "microbial ecology": ["environmental microbiology", "bioremediation", "biotechnology", "biochemistry", "genetic engineering", "fermentation", "mutation"],
        #chapter8

    "cell biology": ["genetics", "biochemistry", "microbiology", "botany", "zoology", "physiology", "molecular biology"],
    "biotechnology": ["genetic engineering", "microbiology", "biochemistry", "pharmacology", "nanotechnology", "virology", "immunology"],
    "genetic engineering": ["biotechnology", "microbiology", "biochemistry", "pharmacology", "nanotechnology", "virology", "immunology"],
    "DNA": ["RNA", "chromosome", "gene", "protein", "enzyme", "nucleotide", "mutation"],
    "RNA": ["DNA", "chromosome", "gene", "protein", "enzyme", "nucleotide", "mutation"],
    "gene": ["DNA", "RNA", "chromosome", "protein", "enzyme", "nucleotide", "mutation"],
    "chromosome": ["DNA", "RNA", "gene", "protein", "enzyme", "nucleotide", "mutation"],
    "mutation": ["variation", "evolution", "adaptation", "natural selection", "artificial selection", "biotechnology", "genetics"],
    "cloning": ["genetic modification", "gene therapy", "mutation", "evolution", "adaptation", "reproduction", "artificial selection"],
    "gene therapy": ["cloning", "genetic modification", "mutation", "evolution", "adaptation", "reproduction", "artificial selection"],
    "stem cells": ["somatic cells", "germ cells", "mutation", "evolution", "adaptation", "biotechnology", "cloning"],
    "recombinant DNA": ["gene therapy", "cloning", "genetic modification", "mutation", "evolution", "biotechnology", "genetics"],
    "genetically modified organisms": ["mutants", "hybrids", "natural selection", "cloning", "gene therapy", "biotechnology", "evolution"],
    "transgenic organisms": ["mutants", "hybrids", "natural selection", "cloning", "gene therapy", "biotechnology", "evolution"],
    "tissue culture": ["cloning", "biotechnology", "genetic engineering", "microbiology", "mutation", "plant breeding", "somatic hybridization"],
    "plant breeding": ["tissue culture", "cloning", "biotechnology", "genetic engineering", "mutation", "somatic hybridization", "hybridization"],
    "hybridization": ["plant breeding", "tissue culture", "cloning", "biotechnology", "genetic engineering", "mutation", "somatic hybridization"],
    "somatic hybridization": ["hybridization", "plant breeding", "tissue culture", "cloning", "biotechnology", "genetic engineering", "mutation"],
    "bioremediation": ["fermentation", "biodegradation", "recycling", "genetic engineering", "biotechnology", "pollution", "mutation"],
    "biodegradation": ["bioremediation", "recycling", "fermentation", "genetic engineering", "biotechnology", "mutation", "pollution"],
    "nanotechnology": ["biotechnology", "microbiology", "genetic engineering", "pharmacology", "virology", "immunology", "medicine"],
    "bioinformatics": ["biotechnology", "microbiology", "genetic engineering", "pharmacology", "virology", "immunology", "medicine"],
    "pharmacogenomics": ["bioinformatics", "biotechnology", "microbiology", "genetic engineering", "pharmacology", "virology", "medicine"],
    "gene sequencing": ["DNA fingerprinting", "PCR", "mutation", "evolution", "genetics", "genetic engineering", "cloning"],
    "DNA fingerprinting": ["gene sequencing", "PCR", "mutation", "evolution", "genetics", "genetic engineering", "cloning"],
    "PCR": ["DNA fingerprinting", "gene sequencing", "mutation", "evolution", "genetics", "genetic engineering", "cloning"],
    "biopharmaceuticals": ["biotechnology", "genetic engineering", "microbiology", "pharmacology", "nanotechnology", "virology", "immunology"],
    "genome": ["chromosome", "DNA", "RNA", "gene", "protein", "enzyme", "mutation"],
    "proteomics": ["genomics", "bioinformatics", "biotechnology", "genetic engineering", "microbiology", "biochemistry", "medicine"],
    "genomics": ["proteomics", "bioinformatics", "biotechnology", "genetic engineering", "microbiology", "biochemistry", "medicine"],
    "synthetic biology": ["biotechnology", "genetic engineering", "microbiology", "pharmacology", "nanotechnology", "virology", "medicine"],
    "biomimetics": ["biotechnology", "genetic engineering", "microbiology", "pharmacology", "nanotechnology", "virology", "medicine"],
    "gene splicing": ["recombinant DNA", "genetic engineering", "mutation", "cloning", "biotechnology", "genetics", "PCR"],
    "stem cell therapy": ["gene therapy", "cloning", "biotechnology", "genetic engineering", "mutation", "evolution", "medicine"],
    "monoclonal antibodies": ["vaccines", "biotechnology", "genetic engineering", "pharmacology", "nanotechnology", "virology", "medicine"],
    "transgenesis": ["cloning", "gene therapy", "mutation", "evolution", "adaptation", "biotechnology", "genetics"],
    "biotechnology applications": ["medicine", "agriculture", "pharmaceuticals", "environment", "bioinformatics", "nanotechnology", "energy"],
    "bioplastics": ["biodegradable polymers", "biotechnology", "nanotechnology", "environment", "bioinformatics", "biopharmaceuticals", "medicine"],
    "biofuels": ["ethanol", "biodiesel", "biogas", "biomass", "fermentation", "biotechnology", "synthetic fuel"],
    "biomass": ["biofuels", "ethanol", "biodiesel", "biogas", "fermentation", "biotechnology", "synthetic fuel"],
    "ethanol": ["biodiesel", "biogas", "biofuels", "biomass", "fermentation", "biotechnology", "synthetic fuel"],
    "biodiesel": ["ethanol", "biogas", "biofuels", "biomass", "fermentation", "biotechnology", "synthetic fuel"],
    "biogas": ["ethanol", "biodiesel", "biofuels", "biomass", "fermentation", "biotechnology", "synthetic fuel"],
    "biotechnology ethics": ["gene therapy risks", "cloning concerns", "genetic privacy", "biosecurity", "bioweapons", "human enhancement", "eugenics"],
    "eugenics": ["gene therapy risks", "cloning concerns", "genetic privacy", "biosecurity", "bioweapons", "human enhancement", "biotechnology ethics"],
        #chapter9

        "social health": ["mental health", "physical health", "emotional health", "personal health", "public health", "community health", "environmental health"],
    "mental health": ["social health", "physical health", "emotional health", "personal health", "public health", "community health", "environmental health"],
    "physical health": ["social health", "mental health", "emotional health", "personal health", "public health", "community health", "environmental health"],
    "emotional health": ["mental health", "social health", "physical health", "personal health", "public health", "community health", "environmental health"],
    "public health": ["social health", "mental health", "physical health", "personal health", "emotional health", "community health", "environmental health"],
    "community health": ["social health", "mental health", "physical health", "personal health", "public health", "emotional health", "environmental health"],
    "environmental health": ["social health", "mental health", "physical health", "personal health", "public health", "community health", "emotional health"],
    "stress": ["anxiety", "depression", "frustration", "mental fatigue", "nervousness", "burnout", "emotional distress"],
    "anxiety": ["stress", "depression", "frustration", "mental fatigue", "nervousness", "burnout", "emotional distress"],
    "depression": ["stress", "anxiety", "frustration", "mental fatigue", "nervousness", "burnout", "emotional distress"],
    "peer pressure": ["social norms", "bullying", "group influence", "social expectations", "conformity", "friendship", "teamwork"],
    "bullying": ["peer pressure", "social norms", "group influence", "social expectations", "conformity", "friendship", "teamwork"],
    "social norms": ["peer pressure", "bullying", "group influence", "social expectations", "conformity", "friendship", "teamwork"],
    "group influence": ["peer pressure", "bullying", "social norms", "social expectations", "conformity", "friendship", "teamwork"],
    "social expectations": ["peer pressure", "bullying", "group influence", "social norms", "conformity", "friendship", "teamwork"],
    "conformity": ["peer pressure", "bullying", "group influence", "social norms", "social expectations", "friendship", "teamwork"],
    "friendship": ["peer pressure", "bullying", "group influence", "social norms", "social expectations", "conformity", "teamwork"],
    "teamwork": ["peer pressure", "bullying", "group influence", "social norms", "social expectations", "conformity", "friendship"],
    "substance abuse": ["alcoholism", "drug addiction", "tobacco use", "opioid abuse", "stimulant misuse", "narcotics addiction", "prescription drug abuse"],
    "alcoholism": ["substance abuse", "drug addiction", "tobacco use", "opioid abuse", "stimulant misuse", "narcotics addiction", "prescription drug abuse"],
    "drug addiction": ["substance abuse", "alcoholism", "tobacco use", "opioid abuse", "stimulant misuse", "narcotics addiction", "prescription drug abuse"],
    "tobacco use": ["substance abuse", "alcoholism", "drug addiction", "opioid abuse", "stimulant misuse", "narcotics addiction", "prescription drug abuse"],
    "opioid abuse": ["substance abuse", "alcoholism", "drug addiction", "tobacco use", "stimulant misuse", "narcotics addiction", "prescription drug abuse"],
    "stimulant misuse": ["substance abuse", "alcoholism", "drug addiction", "tobacco use", "opioid abuse", "narcotics addiction", "prescription drug abuse"],
    "narcotics addiction": ["substance abuse", "alcoholism", "drug addiction", "tobacco use", "opioid abuse", "stimulant misuse", "prescription drug abuse"],
    "prescription drug abuse": ["substance abuse", "alcoholism", "drug addiction", "tobacco use", "opioid abuse", "stimulant misuse", "narcotics addiction"],
    "domestic violence": ["abuse", "harassment", "assault", "neglect", "trauma", "bullying", "oppression"],
    "harassment": ["domestic violence", "abuse", "assault", "neglect", "trauma", "bullying", "oppression"],
    "assault": ["domestic violence", "harassment", "abuse", "neglect", "trauma", "bullying", "oppression"],
    "neglect": ["domestic violence", "harassment", "assault", "abuse", "trauma", "bullying", "oppression"],
    "trauma": ["domestic violence", "harassment", "assault", "neglect", "abuse", "bullying", "oppression"],
    "bullying": ["domestic violence", "harassment", "assault", "neglect", "trauma", "abuse", "oppression"],
    "oppression": ["domestic violence", "harassment", "assault", "neglect", "trauma", "bullying", "abuse"],
    "social inequality": ["poverty", "discrimination", "prejudice", "injustice", "segregation", "racism", "marginalization"],
    "discrimination": ["social inequality", "poverty", "prejudice", "injustice", "segregation", "racism", "marginalization"],
    "prejudice": ["social inequality", "poverty", "discrimination", "injustice", "segregation", "racism", "marginalization"],
    "injustice": ["social inequality", "poverty", "discrimination", "prejudice", "segregation", "racism", "marginalization"],
    "segregation": ["social inequality", "poverty", "discrimination", "prejudice", "injustice", "racism", "marginalization"],
    "racism": ["social inequality", "poverty", "discrimination", "prejudice", "injustice", "segregation", "marginalization"],
    "marginalization": ["social inequality", "poverty", "discrimination", "prejudice", "injustice", "segregation", "racism"],
        #chapter10

    "disaster": ["calamity", "hazard", "emergency", "catastrophe", "tragedy", "accident", "devastation"],
    "natural disaster": ["earthquake", "flood", "cyclone", "tsunami", "landslide", "volcano", "hurricane"],
    "man-made disaster": ["terrorism", "war", "industrial accident", "nuclear disaster", "oil spill", "deforestation", "chemical leakage"],
    "earthquake": ["tsunami", "landslide", "flood", "volcano", "cyclone", "hurricane", "storm"],
    "tsunami": ["earthquake", "flood", "landslide", "volcano", "cyclone", "hurricane", "storm"],
    "flood": ["earthquake", "tsunami", "landslide", "volcano", "cyclone", "hurricane", "storm"],
    "landslide": ["earthquake", "flood", "tsunami", "volcano", "cyclone", "hurricane", "storm"],
    "cyclone": ["earthquake", "flood", "tsunami", "landslide", "volcano", "hurricane", "storm"],
    "hurricane": ["earthquake", "flood", "tsunami", "landslide", "volcano", "cyclone", "storm"],
    "volcano": ["earthquake", "flood", "tsunami", "landslide", "cyclone", "hurricane", "storm"],
    "storm": ["earthquake", "flood", "tsunami", "landslide", "volcano", "cyclone", "hurricane"],
    "wildfire": ["forest fire", "bushfire", "heatwave", "drought", "lightning", "smog", "pollution"],
    "drought": ["heatwave", "desertification", "water scarcity", "climate change", "global warming", "wildfire", "famine"],
    "epidemic": ["pandemic", "outbreak", "infection", "disease", "virus", "quarantine", "isolation"],
    "pandemic": ["epidemic", "outbreak", "infection", "disease", "virus", "quarantine", "isolation"],
    "oil spill": ["pollution", "chemical leakage", "industrial accident", "toxic waste", "radiation", "deforestation", "climate change"],
    "chemical leakage": ["oil spill", "pollution", "industrial accident", "toxic waste", "radiation", "deforestation", "climate change"],
    "nuclear disaster": ["radiation", "Chernobyl", "Fukushima", "fallout", "meltdown", "reactor failure", "atomic explosion"],
    "first aid": ["CPR", "bandage", "wound care", "splint", "tourniquet", "resuscitation", "emergency response"],
    "CPR": ["first aid", "resuscitation", "artificial respiration", "defibrillation", "chest compression", "oxygen therapy", "AED"],
    "defibrillator": ["CPR", "AED", "first aid", "shock treatment", "resuscitation", "electroshock", "heart failure"],
    "disaster management": ["risk reduction", "preparedness", "mitigation", "response", "recovery", "relief", "resilience"],
    "risk reduction": ["disaster management", "preparedness", "mitigation", "response", "recovery", "relief", "resilience"],
    "preparedness": ["disaster management", "risk reduction", "mitigation", "response", "recovery", "relief", "resilience"],
    "mitigation": ["disaster management", "risk reduction", "preparedness", "response", "recovery", "relief", "resilience"],
    "response": ["disaster management", "risk reduction", "preparedness", "mitigation", "recovery", "relief", "resilience"],
    "recovery": ["disaster management", "risk reduction", "preparedness", "mitigation", "response", "relief", "resilience"],
    "relief": ["disaster management", "risk reduction", "preparedness", "mitigation", "response", "recovery", "resilience"],
    "resilience": ["disaster management", "risk reduction", "preparedness", "mitigation", "response", "recovery", "relief"],
    "evacuation": ["safety drill", "rescue operation", "emergency exit", "escape plan", "fire drill", "relocation", "displacement"],
    "search and rescue": ["evacuation", "emergency response", "firefighting", "medical aid", "disaster relief", "aid distribution", "casualty management"],
    "firefighting": ["search and rescue", "emergency response", "medical aid", "disaster relief", "aid distribution", "casualty management", "evacuation"],
    "casualty management": ["search and rescue", "emergency response", "firefighting", "medical aid", "disaster relief", "aid distribution", "evacuation"],
    "emergency services": ["fire department", "ambulance", "police", "disaster response", "paramedics", "hospital", "rescue team"],
    "ambulance": ["emergency services", "paramedics", "fire department", "hospital", "disaster response", "rescue team", "medical aid"],
    "paramedics": ["emergency services", "ambulance", "fire department", "hospital", "disaster response", "rescue team", "medical aid"],
    "fire department": ["emergency services", "ambulance", "paramedics", "hospital", "disaster response", "rescue team", "medical aid"],
    "police": ["law enforcement", "security forces", "emergency services", "crime prevention", "public safety", "rescue team", "first responders"],
    "first responders": ["paramedics", "firefighters", "police", "disaster response", "emergency services", "rescue team", "aid workers"],
    "aid workers": ["first responders", "disaster response", "relief organizations", "volunteers", "NGOs", "humanitarian efforts", "medical teams"],
    "NGOs": ["aid workers", "relief organizations", "volunteers", "humanitarian efforts", "charity", "disaster response", "international agencies"],
    "international agencies": ["NGOs", "UN", "WHO", "Red Cross", "disaster response", "humanitarian efforts", "global relief"],
    "Red Cross": ["international agencies", "UN", "WHO", "disaster response", "humanitarian efforts", "global relief", "charity"],
    "WHO": ["international agencies", "UN", "Red Cross", "disaster response", "humanitarian efforts", "global relief", "charity"],
    "UN": ["WHO", "Red Cross", "international agencies", "disaster response", "humanitarian efforts", "global relief", "charity"],
    "sustainable development": ["climate action", "disaster preparedness", "environmental protection", "economic growth", "social justice", "green technology", "renewable energy"]



    }

    # Additional general science distractors
    general_science_distractors = [
        # Physics concepts
    "Newton's laws", "gravitation", "friction", "momentum", "inertia", "work", "energy", "power",
    "velocity", "acceleration", "projectile motion", "circular motion", "simple harmonic motion",
    "light reflection", "light refraction", "lenses", "dispersion", "diffraction", "interference",
    "Doppler effect", "sound waves", "resonance", "beats", "electromagnetic spectrum", "magnetism",
    "electromagnetism", "electric current", "resistance", "Ohm's law", "potential difference",
    "electric circuits", "Joule's law", "electric power", "transformers", "generators", "motors",
    "semiconductors", "digital electronics", "Boolean logic", "nuclear fission", "nuclear fusion",

    # Chemistry concepts
    "periodic table", "atomic structure", "electronic configuration", "valency", "chemical bonding",
    "ionic bond", "covalent bond", "metallic bond", "alloys", "acids", "bases", "salts", "pH scale",
    "neutralization", "redox reactions", "electrolysis", "corrosion", "galvanization", "catalysts",
    "organic compounds", "hydrocarbons", "functional groups", "polymers", "plastics", "alcohols",
    "carboxylic acids", "esters", "soaps", "detergents", "chemical equilibrium", "Le Chatelier's principle",
    "rate of reaction", "collision theory", "activation energy", "enthalpy", "entropy", "free energy",

    # Biology concepts
    "cell structure", "cell organelles", "nucleus", "mitochondria", "chloroplasts", "ribosomes",
    "photosynthesis", "respiration", "fermentation", "digestion", "absorption", "assimilation",
    "excretion", "homeostasis", "nervous system", "endocrine system", "hormones", "circulatory system",
    "respiratory system", "immune system", "skeletal system", "muscular system", "reproduction",
    "genetics", "heredity", "Mendel's laws", "DNA structure", "protein synthesis", "genetic engineering",
    "evolution", "natural selection", "adaptation", "biodiversity", "ecosystems", "food chain",
    "trophic levels", "ecological pyramid", "symbiosis", "competition", "predation", "parasitism",

    # Environmental science
    "global warming", "climate change", "ozone depletion", "greenhouse effect", "acid rain",
    "deforestation", "desertification", "sustainable development", "renewable resources",
    "non-renewable resources", "wildlife conservation", "habitat preservation", "endangered species",
    "biodiversity hotspots", "ecological footprint", "carbon footprint", "environmental impact",
    "solid waste management", "bioremediation", "phytoremediation", "ecological succession",
    "carrying capacity", "biogeography", "biosphere reserves", "national parks", "sanctuaries"
    ]

    # Correct answer keywords for matching
    correct_lower = correct_answer.lower()
    predefined_distractors = []

    # Check if any key word from our distractor dict is in the correct answer
    for key in water_cycle_distractors:
        if key in correct_lower:
            predefined_distractors = water_cycle_distractors[key]
            break

    # If we found predefined distractors, use them
    if predefined_distractors:
        # Filter out any that might match the correct answer
        filtered = [d for d in predefined_distractors
                   if d.lower() not in correct_lower and correct_lower not in d.lower()
                   and d not in distractors]

        # Shuffle to get different distractors each time
        random.shuffle(filtered)

        # Add new distractors until we have 3
        for d in filtered:
            if len(distractors) < 3:
                distractors.append(d)
            else:
                break

    # If we don't have enough distractors yet, add from general science
    if len(distractors) < 3:
        # Shuffle general distractors
        random.shuffle(general_science_distractors)

        for distractor in general_science_distractors:
            if (distractor not in distractors and
                distractor.lower() != correct_answer.lower() and
                distractor.lower() not in correct_lower and
                correct_lower not in distractor.lower()):
                distractors.append(distractor)
                if len(distractors) >= 3:
                    break

    # If still not enough, add backup generic distractors
    backup_distractors = ["climate change", "water pollution", "ocean currents",
                         "groundwater", "humidity", "watershed", "weather patterns",
                         "acid rain", "greenhouse effect", "soil erosion", "plate tectonics"]

    while len(distractors) < 3:
        if not backup_distractors:
            break
        distractor = backup_distractors.pop(0)

        if (distractor not in distractors and
            distractor.lower() != correct_answer.lower()):
            distractors.append(distractor)

    return distractors[:3]

# Function to format the MCQ - IMPROVED to ensure uniqueness
def format_mcq(question, correct_answer, distractors):
    # Clean up question
    question = question.strip()
    if not question.endswith('?'):
        question += '?'

    # Make sure all options are unique
    # First, make sure distractors don't match the correct answer
    distractors = [d for d in distractors if d.lower() != correct_answer.lower()]

    # Then make sure distractors don't match each other
    unique_distractors = []
    for d in distractors:
        if not any(d.lower() == ud.lower() for ud in unique_distractors):
            unique_distractors.append(d)

    # If we don't have enough unique distractors, add generic ones
    extra_distractors = ["biological process", "geological phenomenon", "atmospheric event",
                         "chemical reaction", "physical transformation", "natural occurrence",
                         "planetary system", "environmental factor", "ecological process"]

    while len(unique_distractors) < 3:
        if not extra_distractors:
            # If we've exhausted our list, create numbered options
            fake_distractor = f"Option {len(unique_distractors) + 1}"
            unique_distractors.append(fake_distractor)
        else:
            # Try the next extra distractor
            extra = extra_distractors.pop(0)
            if (extra.lower() != correct_answer.lower() and
                not any(extra.lower() == ud.lower() for ud in unique_distractors)):
                unique_distractors.append(extra)

    # Create options list and shuffle
    options = [correct_answer] + unique_distractors[:3]
    random.shuffle(options)

    # Format output
    mcq = f"Question: {question}\n\n"
    for i, option in enumerate(['A', 'B', 'C', 'D']):
        mcq += f"{option}) {options[i]}\n"

    # Add correct answer (hidden)
    correct_option = chr(65 + options.index(correct_answer))  # A, B, C, or D
    mcq += f"\nCorrect Answer: {correct_option}) {correct_answer}"

    return mcq

# Track questions to avoid repetition across all generated questions
global_used_questions = set()
global_used_answers = set()

# Function to generate multiple MCQs from a paragraph - IMPROVED to avoid duplications
def generate_multiple_mcqs(paragraph, num_questions=5):
    all_mcqs = []

    # Try to generate the requested number of MCQs
    attempts = 0
    max_attempts = num_questions * 10  # Allow more attempts in case of failures

    while len(all_mcqs) < num_questions and attempts < max_attempts:
        attempts += 1
       # print(f"Attempt {attempts}...")

        # Generate a raw question
        raw_question_output = generate_question(paragraph)

        # Parse the raw output
        parsed = parse_question_output(raw_question_output)
        question = parsed["question"]

        # Skip if we've already used this question or a similar one
        question_lower = question.lower()
        if any(question_lower == similar_question for similar_question in global_used_questions):
          continue

        correct_answer = parsed["correct_answer"]
        existing_distractors = parsed["distractors"]

        # If no correct answer was found, generate one
        if not correct_answer:
            # Try to generate a correct answer
            input_text = f"Based on this text: {paragraph}. What is the correct answer to this question: {question}? Give a short, concise answer only."
            input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)

            output = model.generate(
                input_ids,
                max_length=20,
                do_sample=True,
                temperature=0.5
            )
            raw_answer = tokenizer.decode(output[0], skip_special_tokens=True).strip()
            correct_answer = extract_key_answer(raw_answer)

        # Skip if we couldn't get a valid answer or if it's a duplicate
        if not correct_answer:
            continue

        # Check if this answer is too similar to a previous one
        correct_lower = correct_answer.lower()
        if any(similar_answer in correct_lower or correct_lower in similar_answer
               for similar_answer in global_used_answers):
            continue

        # Generate distractors if needed
        if len(existing_distractors) < 3:
            distractors = create_distractors(paragraph, correct_answer, existing_distractors)
        else:
            # Clean up any trailing characters (like '|')
            distractors = [d.rstrip('| ') for d in existing_distractors[:3]]

        # Format the MCQ
        formatted_mcq = format_mcq(question, correct_answer, distractors)

        # Add to our list and mark question and answer as used
        all_mcqs.append(formatted_mcq)
        global_used_questions.add(question_lower)
        global_used_answers.add(correct_lower)

        # Print progress
        print(f"Generated {len(all_mcqs)}/{num_questions} MCQs...")

    return all_mcqs
