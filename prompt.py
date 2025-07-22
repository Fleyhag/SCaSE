class prompt_test:
    pt_screen="""You are a scientist specializing in alloys. Please read the following text from an alloy journal article. 
    "paper_text": <{paper_text}>
    Output "True" or "False" following the 4 judgments:
    1. Determine whether this article is a part of an "article", not a "review", "comment", or something else. If the text is not a part of an "article", output "False".
    2. If the article is specifically about steel or titanium alloy, it's valid. Else, output "False".
    3. If the article include tensile testing, it's valid. Else, output "False".
    4. If 3 is satisfied, and if material that underwent the tensile testing is homogenous, it's valid. Else, output "False". Note: multi-phase alloys are considered homogenous.
    If all 4 judgments are satisfied, output "True".
    Output "True" or "False" directly without any additional text or symbols."""

    pt_abbr="""INPUT;{{"paper_text": <{paper_text}>}}
    INSTRUCTIONS;
    Output all the "abbreviations" defined in the text. "Abbreviation" is a short form of a word or phrase. Element (e.g. Fe, Co, C) are no need. The abbreviation should be followed by its full form in JSON format. For example, [{{"abbr": "EBSD", "full": "Electron Backscatter Diffraction"}},...].
    Output the result directly without any additional text or symbols.
    """

    pt_text="""INPUT:{{"paper_text": <{paper_text}>}}
    INSTRUCTIONS:
    Translate and categorize article sections into "introduction", "method", and "result". Group all experiment-related sections under "method", like "experimental", "materials". Place all results, discussion sections under "result". Exclude other sections such as conclusion, author contributions, acknowledgements, funding. 
    OUTPUT FORMAT:
    Output JSON format directly without any additional text or symbols: {{"introduction":["section_i"...],"method": ["section_i"...],"result": ["section_i"...]}}
    Attention: output JSON formatted plaintext without any additional text or symbols!
    """

    pt_figs='''INPUT:
    "figure_caption": <{fa}>
    "paper_text": <{paper_text}>
    
    INSTRUCTION:
    For each figure:
        a) Locate ALL mentions in "paper_text" (e.g., "Fig. 1", "Figure 2")
        b) Extract the surrounding 3-sentence context window
        c) Identify key classification according to the figure title and context
        d) DROP the rest figures that cannot be classified.

    Classification rules:
    - "tensile_sample_fig"
        - figs that describe the size of sample used in tensile test. "NONE" if unavailable.
    - "tensile_result"
        - "stress-strain_curve": 
            - also include curves that can be converted into strss-strain curve, such as force-time curve, force-displacement curve.
        -"other_tensile_result"
            - figs concerning tensile test result, but are not specific curve. such as scattering fig.
    - "microstructure"
        - "EBSD_fig": 
            - include IPF coloring, BC(Band Contrast), GB(grain boundary), KAM(Kernel Average Misorientation), GND(geometrically necessary dislocations), and phase map.
            - DO NOT include: the microstructure of fracture surface; the elemental distribution such as EDS; other methods such as XRD, DSC, etc.
        - "phase_map_fig": 
            - phase distribution map should be included. It should be noted that the phase distribution map is not the same as the phase map.
            - usually there are concise phase names in the figure title.
        - "microscope_fig": 
            - include characterization method such as metallographic micrograph, optical micrograph, SEM (Scanning Electron microscopy), TEM (Transmission electron microscopy), etc. More specialized characterization methods should also be included, such as FESEM (Field Emission Scanning Electron morphologys), HRTEM (High-Resolution Transmission Electron morphologys).
            - exclude morphology description, such as: Crack, Inclusion, Porosity, Surface defect, Hole, Edge Crack, Fracture etc.
            - exclude other characterizations: the elemental distribution such as EDS; other methods such as XRD, DSC, etc.
        - "other_microstructure": The rest figures.

    Output JSON format directly without any additional text or symbols: {{"tensile_sample_fig":[{{"figure": "xxx(number)","title": "xxx(complete figure title)"}}...],
    "tensile_result":{{
        "stress-strain_curve":[...],
        "other_tensile_result":[...]
        }}
    "microstructure":{{
        "EBSD_fig": [...], 
        "phase_map_fig":[...], 
        "microscope_fig":[...],
        "other_fig": [...]
        }}
    }}
    '''

    pt_pbf="""INPUT:
    "paper_text": <{method}>

    INSTRUCTION:
    Classify powder bed fusion (PBF) technologies:
    1. PBF CORE CRITERIA (ALL required):
    - Powder bed-based process
    - Layer-by-layer fusion
    - Stationary powder (no feeding during fusion)
    2. ENERGY SOURCE SUBTYPES:
    A) Laser-based PBF (LPBF/SLM/DMLS):
        - Indicators: "laser", "scan strategy", ≤1500W power
        - Layer thickness typically 20-100μm
    B) Electron beam PBF (EBM):
        - Indicators: "electron beam", "EBM", "vacuum"
        - Layer thickness typically 50-200μm
        - Preheating (600-1100°C) mentioned
    3. AUTOCLASSIFICATION RULES:
    - If "selective laser melting" | "SLM" → PBF-Laser
    - If "electron beam melting" | "EBM" → PBF-EBM
    - If "DED" | "LENS" | "wire arc" → NON-PBF
    4. PBF NEGATIVE INDICATORS (ANY triggers FALSE):
    - Dynamic powder parameters:
        * "powder feeding rate" 
        * "carrier gas flow"
        * "nozzle diameter"
    - Deposition rate >500g/h
    - Chamber pressure >1atm
    - Multi-axis deposition head movement
    5. OUTPUT FORMAT:
    Output JSON format directly without any additional text or symbols:
    {{
        "is_PBF": <TRUE|FALSE>,
        "subtype": <"Laser"|"Electron_beam"|"Unspecified"|"N/A">,
        "evidence": ["key_term1", "key_term2"]
    }}
    """

    pt_composition="""INPUT:
    "paper_text": <{method}>
    "tables": <{tables}>
    INSTRUCTIONS:
    Extract all the "composition". "Composition" may also be referred to as "compositions", "content", "component", "element", and "percentage".
    "Composition" includes the "composition name", "alloy type", and "composition content". Here are the explanations for each:
    - "composition_content" is the percentages of all the elements in an alloy. The main elements can be replaced with "bal." or "balanced" instead of specific percentages. The unit "%" is needed. If the original text is a range, keep the range, for example: "Ti: 3.0-3.5%".
    - "composition name" can be found in the context. If the composition does not have a "composition name", name it as "composition_1", "composition_2", "composition_3", etc.
    - "alloy type" is usually the main element, e.g., "steel", "titanium". If the alloy does not have a main element, check the context to see how the authors refer to their alloy.
    "Composition" is typically found in the "methods" or "experiment" sections that describe the experimental methods. In many cases, it is listed in a table. If the composition is characterized using methods like EDS, use the composition mentioned in the methods section, NOT the characterization results.
    OUTPUT FORMAT:
    Output JSON format directly without any additional text or symbols:
    {{"composition_name": "xxx", "alloy_type": "xxx", "composition_content": "xxx"}}
    EXAMPLE:
    Original text: Thermo Jarrell Ash Spark Emission Spectroscope was used to examine the chemical composition of as-received 13-4 MSS which was found to be 0.07 C, 13.51 Cr, 3.35 Ni, 0.62 Mn, 0.64 Si, 0.02 S, 0.06 Cu, 0.01 P, 0.32 Mo, and balanced Fe by wt.%.
    Answer: {{"composition_name": "13-4 MSS", "alloy_type": "steel", "composition_content": ["C: 0.07%", "Cr: 13.51%", "Ni: 3.35%", "Mn: 0.62%", "Si: 0.64%", "S: 0.02%", "Cu: 0.06%", "P: 0.01%", "Mo: 0.32%", "Fe: bal."]}}
    Attention: All the values must be extracted directly from the provided text, and not inferred from external knowledge or calculated or estimated values. If the composition is not mentioned in the text, fill in "NONE".
    """

    pt_conditions=""""INPUT:
    "paper_text": <{method}>
    "figure_captions": <{fa}>
    "tables": <{tables}>
    "is_PBF": <{is_PBF}>
    
    INSTRUCTION:
    Extract all the following 5 descriptions from the "paper_text", "figure_captions", and "tables". 
    1. look for "printing parameter" :
    - If "is_PBF" is FALSE, use "printing_parameter":"NONE".
    - If "is_PBF" is TRUE", look for informations about:
        -"equipment": machinery used for 3D printing;
        -"laser_power": value & unit for laser systems; 'NONE' otherwise;
        -"beam_current": value & unit for electron beam systems; 'NONE' otherwise;
        -"accelerating_voltage": value + unit for electron beam systems; 'NONE' otherwise;
        -"scan_speed": value & unit; 'NONE' if unavailable;
        -"layer_thickness": value & unit; 'NONE' if unavailable;
        -"hatch_spacing": value & unit; 'NONE' if unavailable;
        -"rotation_angle": value + '°'; 'NONE' if unavailable;
        -"scan_strategy": description of scan pattern; 'NONE' if unavailable.
    2. look for "tensile_condition":
    - "tensile standard"(test method such as ASTM E8), 
    - "tensile temperature"(default is room temperature), 
    - "tensile speed"(aka "strain rate"), 
    - "sample shape" (aka "gauge length", "cross-sectional area")       
        - "text": (extract from "paper_text")
        - "figure": (use "figure_captions["tensile_sample_fig"]")
    - "tensile direction"(horizontal, vertical, Y-axis,etc.). 
    - Do NOT extract the conditions that are not about tensile test, e.g. hardness test conditions should be ignored.
    3. look for "fabrication_process":
    - "fabrication_process" include: forge, wrought, melting, or molding, etc.
    4. look for "thermal_processes":
    - "thermal_process" include: annealing and aging, solution treatment, tempering, normalizing, sintering, precipitation hardening, case hardening,  stress relieving, as-annealed, direct aged, etc.
    - Great attention!!! The order in the description of the "thermal_process" in the original text is necessary, because the previous steps are sometimes omitted when describing what heat treatment the sample underwent.
    5. look for "other_process":
    - "other_process" include: sometimes DURING the "thermal_process" process, but not strictly belong to "thermal_process", such as "rolling", "electroplate", etc.
    
    OUTPUT FORMAT:
    Output JSON format directly without any additional text or symbols: {{"printing_parameter": "xxx(str)", "tensile_condition": "xxx(str)", "fabrication_process": "xxx(str)", "thermal_process": "xxx(str)", "other_process": "xxx(str)"}}
    where "xxx" should use the original text"s phrasing as much as possible. If the information is presented in a table, you can summarize the extraction result in a list or json list. Default value of "xxx" is "NONE".
    """

    # 根据前两个问题的回答，提取所有测过拉伸的‘样品’
    pt_msu1="""Given:
    "paper_text": <{paper_text}>
    "captions": <{classified_figures}>
    "tables": <{tables}>
    "composition_info": <{composition}>
    "manufacture_info": <{conditions}>

    Instructions:
    1. Tensile_result detection:
    - From "paper_text", "captions" "tables", look for "stress-strain curves"(already classified in "captions"), "yield strength", "ultimate strength(aka tensile strength)", "fracture elongation", "uniform elongation", and "fracture toughness".
    2.  Sample association:
        - Link tensile_result to samples according to context
        - Link samples to their composition/process parameters(complete the composition/process parameters according to "composition_info"/"manufacture_info"
    3. Data extraction:
        - Extract content/size values with units
        - Preserve original sentence or figure/table number+titile

    Output Specification:
    Output JSON format directly without any additional text or symbols:
    [{{
        "sample_name": (extracted from the context), "composition_name": "xxx", "printing_parameter": "xxx", "tensile_condition": "xxx", "thermal_process": "xxx", "other_process": "xxx",
        }},
        "tensile_property": {{
            "stress_strain_curve": ["Figure number+titile"...], 
            "yield_strength": X+unit, NONE if unavailable,
            "ultimate_strength": X+unit, NONE if unavailable,
            "fracture_elongation": X %, NONE if unavailable,
            "uniform_elongation": X %, NONE if unavailable,
            "fracture_toughness": X+unit, NONE if unavailable
        }}
    }}...]

    Attention:
    - **Consistency in Sample Identification**: (ensure (each sample) (listed separately) (based-on unique processing-conditions) (even-if same-material) (different-conditions -> different-samples) (after generating-info) (check conditions correct) (no incorrect merging))
    - **Consistency in "Thermal_process"**: ensure in the correct sequence. 
    - **Some thermal_process steps may be omitted**: e.g. if a sample is called as "460 aged", but the methods section explicitly states that all samples were first subjected to annealing, then the correct thermal process should be firstly annealed and then 460 aged.
    - **Consistency in figure number**: double-check the figure number and figure content according to "captions", ensure each figure number match its description.
    - All values extracted **directly from the original text or table**: not inferred from external knowledge or calculated or estimated values. Do NOT look for value in figures.
    """

    pt_msu2="""Input:
    "paper_text": <{paper_text}>
    "captions": <{classified_figures}>
    "composition_info": <{composition}>
    "manufacture_info": <{conditions}>

    Instruction:
    Identify and extract all "samples" and their microstructure images. "Samples" are distinguished by different compositions or manufacturing processes.
    Follow these steps:
    1. Examine each "caption" to determine if it belongs to microstructure or phase images(if the images are pre-classified, double check the classification):
    - "microscope": Includes scanning electron microscope (SEM), transmission electron microscope (TEM), optical microscope (OM), metallographic microscope images, but excludes elemental distribution like EDS; other methods like XRD, DSC, etc.
    - "ebsd_image": Includes characterization images obtained through Electron Backscatter Diffraction (EBSD), specifically:
      [Orientation Color Map, Inverse Pole Figure (IPF), Kernel Average Misorientation (KAM), Grain Boundary (GB) map, Geometrically Necessary Dislocation (GND) Density map, Phase Map, Band Contrast]
    2. For images identified in step 1, filter out those tested after stretching or showing fracture after stretching
    3. For retained images, identify each "sample" and trace the context in "paper_text" to match each sample's "composition" and "manufacturing process"
    4. For samples found in step 3, merge only if they have identical composition and manufacturing process, otherwise list separately

    Output format:
    Output directly in JSON format without any additional text or symbols: [{{"sample_name": "xxx", "composition_name": "xxx", "printing_parameter": "xxx", "tensile_condition": "xxx", "thermal_process": "xxx", "other_process": "xxx", "microscope":"xxx", "EBSD_image": "xxx"}} ...]
    Where:
    - "sample_name": Extracted from context, e.g., "Three groups of original DP980 (DP980-Orig) specimens were heated at 250, 400 and 550 °C for 60 min respectively and air cooled afterwards. They are referred to herein as DP980-250, DP980-400, and DP980-550 respectively." In this case, there are 4 samples
    - "microscope"(figure number)
    - "EBSD_image"(figure number)
    - Default value "xxx" is "NONE"

    Attention:
    - **Figure number consistency**: Carefully verify figure numbers match their descriptions according to "captions"
    - **Sample identification consistency**: Ensure each sample is listed separately based on unique manufacturing conditions (even with same composition, different conditions count as different samples), check conditions are correct after generation, avoid incorrect merging
    - **Thermal process sequence consistency**: Ensure correct process sequence
    - **Possibly omitted thermal process steps**: E.g. if a sample is called "460 aged" but manufacture_info explicitly states all samples were first annealed, then the correct thermal process should be annealed first then 460 aged
    - All values must be extracted directly from original text or tables, not inferred from external knowledge, calculated, estimated, or obtained from figures
    """
    
    # 提取所有相信息
    pt_msu3="""Input:
    "paper_text": {paper_text}
    "captions": {classified_figures}
    "tables": {tables}
    "composition_info": {composition}
    "manufacture_info": {conditions}
    "phase_library": {{
        "matrix_phases": ["α", "α'", "α''", "γ", "ε", "θ", "ferrite", "austenite", "martensite", "pearlite", "bainite", "cementite","retained austenite", "tempered martensite"],
        "precipitates": ["M23C6", "TiC", "NbC", "VC", "Fe3C", "MN", "AlN", "TiN", "Cu-rich", "ε-Cu", "M7C3", "M6C", "MC", "M2C", "M3C", "M(C,N)", "NbN", "VN", "Ni3Ti", "Ni3Al", "Fe2Mo", "Fe2Nb", "Fe2Ti","TiC", "NbC", "VC", "Cr23C6", "Mo2C", "W2C", "Fe3C", "Fe5C2", "κ-carbide", "η-carbide"],
        "symbol_mapping": {{"α": "ferrite","γ": "austenite","α'": "martensite","θ": "cementite","ε": "epsilon-martensite"}}
    }}

    Instruction:
    Comprehensively identify and extract all "samples" with their phase and precipitate information. "Samples" are distinguished by unique composition or manufacturing process combinations.
    Execution Protocol:
    1. PHASE IDENTIFICATION:
    - Scan text for any term matching "phase_library"
    - Prioritize paper's own definitions over predefined mappings
    - Record both original notation and standardized name

    2. PROCESSING STEPS:
    a) Phase detection:
        - Match terms against "phase_library"
        - Resolve symbols using "symbol_mapping"
    b) Sample association:
        - Link phases to samples according to context
        - Link samples to their composition/process parameters(complete the composition/process parameters according to "composition_info"/"manufacture_info"
    c) Data extraction:
        - Extract content/size values with units
        - Preserve original sentence or figure/table number+titile

    Output Specification:
    [{{
        "sample_name": (extracted from the context), "composition_name": "xxx", "printing_parameter": "xxx", "tensile_condition": "xxx", "thermal_process": "xxx", "other_process": "xxx",
        }},
        "phase_analysis": [{{
            "phase_name": "string",
            "content": "X% (exact value from source)",
            "distribution": "description if available",
            "morphology": "description if available",
            "source": "exact text or Figure/Table number+titile"
            }}...],
        "precipitates": [{{
            "type": "string",
            "size": "X nm (range acceptable if specified)",
            "density": "X m^-3",
            "distribution": "description if available",
            "source": "exact text or Figure/Table number+titile"
            }}...]
    }}...]

    Validation Rules:
    1. Source Verification:
    - Every data point must have traceable source
    - Prefer precise number > inprecise discription
    2. Phase Content Rules:
    - Sum of phase percentages ≤ 100% per sample
    - "Traces" can be used instead of specific number.
    3. Precipitate Rules:
    - Size/density must include units
    - Ranges must be preserved (e.g., "5-10 nm")
    4. Thermal Process Sequencing:
    - Must maintain chronological order
    - Must include implicit steps (e.g., solution treatment before aging)

    Prohibited Actions:
    - NEVER infer phase existence from composition alone
    - NEVER calculate phase percentages from micrographs
    - NEVER assume precipitate types based on composition
    - NEVER combine samples with different thermal histories

    Exception Handling:
    - Conflicting phase reports → create separate entries "source_1"
    - Missing information: keep the key and use "NONE" as value
    """

    pt_merge_msu="""INPUT 
    "tensile samples": <{msu1}>
    "microstructure samples" : <{msu2}>
    "phase samples": <{msu3}>

    INSTRUCTION:
    1. merge the sample from "tensile samples", "microstructure samples", and "phase samples". 
    - mathcing rule: ["sample_name", "Composition Name", "Printing parameter", "Thermal process", "Tensile condition"]
    2.screen the merged sample, If no "tensile property", or all contents ["stress_strain_curve","yield_strength","ultimate_strength","fracture_elongation","uniform_elongation",  "fracture_toughness"] in "tensile property" are "none", it should be dropped.

    Output format:
    Output JSON format directly without any additional text or symbols:
    [{{
        "sample_id":"xxx", 
        "sample_name": "xxx", 
        "composition_name": "xxx", 
        "printing_parameter": "xxx", 
        "tensile_condition": "xxx", 
        "thermal_process": "xxx", 
        "other_process": "xxx",
        "tensile_property": "xxx",
        "microscope":"xxx",  
        "EBSD_image": "xxx",
        "phase_analysis": "xxx", 
        "precipitates": "xxx"
    }},...]
    Where:
    - "sample_id": The format is "{file_name}_i", for example, "{file_name}_1", "{file_name}_2", "{file_name}_3"...
    - "xxx": keep original structure from "tensile samples", "microstructure samples", and "phase samples".
    """
    
    pt_structure1="""### Input:
    "sample_info": <{samples}>
    "composition_info": <{composition}>

    ### **Instruction**  
    Convert the input data into a **strictly formatted JSON array** following the exact schema and rules below. Output **ONLY the raw JSON** without any additional text or explanations.  

    ### **Required JSON Structure**  
    [{{
        "sample_id": "string (exact value from sample_info, preserving original capitalization/symbols)",
        "sample_name": "string (exact value from sample_info)",
        "composition_name": "string (from composition_info)",
        "alloy_type": "string (from composition_info)",
        "composition_content": [
            {{
                "element": "string (elemental symbol only, e.g., 'C' instead of 'carbon')",
                "content": "string (value with '%' unit or description text)"
            }}
        ]
    }},...]

    Attention: following instructions should be double checked:
    1. If the original text is a range, keep the range
    2. Even if multiple samples have the same composition, do not omit them; list all of them.
    3. Verify that each component is an element, and remove any components that are not elements, such as "austenite".
    4. Ensure that each component is represented by its elemental symbol; change full names to symbols, e.g., change "carbon" to "C".
    5. Check if there is an element corresponding to "alloy_type" in the components; if not, add the appropriate element with its content marked as "bal." For example, if "alloy_type" is "steel", this indicates the primary element is Fe, so if the list of components does not include Fe, then add "Fe": "bal.".
    """


    pt_structure2="""### Input
    "sample_info": <{samples}>, 
    "is_PBF": <{is_PBF}>, 
    "manufacture_info": <{conditions}>

    ### **Instruction**  
    Convert the input data into a **strictly formatted JSON array** following the exact schema and rules below. Output **ONLY the raw JSON** without any additional text or explanations.  

    ### **Required JSON Structure**  
    [{{
        "sample_id": "string (exact value extracted from sample_info, preserving original capitalization/symbols)",
        "printing_parameter": ('NONE' if "is_PBF" is False or unavailable)
        {{
            "equipment": "string (machinery used for 3D printing)",
            "laser_power": "string (value + unit for laser systems; 'NONE' otherwise)",
            "beam_current": "string (value + unit for electron beam systems; 'NONE' otherwise)",
            "accelerating_voltage": "string (value + unit for electron beam systems; 'NONE' otherwise)",
            "scan_speed": "string (value + 'mm/s'; 'NONE' if unavailable)",
            "layer_thickness": "string (value + 'µm'; 'NONE' if unavailable)",
            "hatch_spacing": "string (value + 'µm'; 'NONE' if unavailable)",
            "rotation_angle": "string (value + '°'; 'NONE' if unavailable)",
            "scan_strategy": "string (description of scan pattern; 'NONE' if unavailable)"
        }},
        "tensile_condition": {{
            "tensile_standard": "string (e.g., 'ASTM E8/E8M'; 'NONE' if unavailable)",
            "tensile_temperature": "string (e.g., 'Room temperature', '100°C'; 'NONE' if unavailable)",
            "tensile_speed": "string (value + 'mm/min'; 'NONE' if unavailable)",
            "tensile_direction": "string (e.g., 'Horizontal'; 'NONE' if unavailable)",
            "sample_shape": {{"text":"string (exact text from sample_info)", "figure": ["string (figure reference in 'Fig. X' format, e.g., ['Fig. 3'])"]}}
        }}
    }},...]

    ### **Critical Rules**  
    1. **Printing Parameters**:  
    - Set entire "printing_parameter" object to "NONE" if "is_PBF" is False.  
    - Always include units (e.g., "mm/s", "µm", "°").  
    - Preserve original ranges if present (e.g., "50-100 µm").  
    2. **Tensile Conditions**:  
    - For "sample_shape", use "Fig. X" format if referring to a figure (main figure only).  
    - Temperature values must include units (°C/°F) or state "Room temperature".  
    3. **Missing Data**:  
    - Use "NONE" (lowercase) for all unavailable fields.  
    4. **Validation**:  
    - Reject if:  
        - Any required field is missing or renamed.  
        - Units are omitted from numerical values.  
        - Figure references deviate from "Fig. X" format.  

    ### **Output**  
    ONLY the raw JSON array as shown above, with no extra text, markdown, or comments."""

    pt_structure3="""### **Input**  
    {{"sample_info": <{samples}>}}  

    ### **Instruction**  
    Convert "sample_info" into a **strictly formatted JSON array** following the exact schema and rules below. Output **ONLY the raw JSON** without any additional text or explanations.  

    ### **Required JSON Structure**  
    [{{
        "sample_id": "string (exact value extracted from sample_info, preserving original capitalization/symbols)",
        "tensile_properties": {{
        "stress_strain_curve": ["string (image reference in 'Fig. X' format, e.g., ['Fig. 3']; omit sub-figures like 'Fig. 2a')"],
        "yield_strength": "string (value + unit; ranges as '350-400 MPa'; uncertainties as '120±5 MPa'; 'NONE' if unavailable)",
        "ultimate_strength": "string (same rules as yield_strength)",
        "fracture_elongation": "string (percentage value, e.g., '15.2%' or '10±2%')",
        "uniform_elongation": "string (same rules as fracture_elongation)",
        "fracture_toughness": "string (e.g., '25 MPa·√m' or 'NONE')"
        }},
        "microstructure": {{
        "microscope": ["string (same 'Fig. X' format as stress_strain_curve)"],
        "EBSD_image": ["string (same 'Fig. X' format)"],
        "phase_analysis": [
            {{(preserve original structure)}}
        ],
        "precipitates": [
            {{(preserve original structure)}}
        ]
        }}
    }},...]

    ### **Critical Rules**  
    1. **Image References** ("stress_strain_curve", "microscope", "EBSD_image"):  
    - Format: "["Fig. X"]" (main figure number only; **never** "Figure 1a" or "Fig. 2b").  
    - Example: "["Fig. 3"]" (valid) | "["Fig. 1", "Fig. 2"]" (for multiple images).  
    2. **Numerical Values** ("*_strength", "*_elongation", "fracture_toughness"):  
    - **Mandatory units**: Always include units (e.g., "MPa", "%", "MPa·√m").  
    - Ranges/uncertainties: Use "350-400 MPa" or "120±5 MPa".  
    - Missing data: Use ""NONE"" (lowercase).  
    3. **Empty Fields**:  
    - Empty arrays allowed for "phase_analysis"/"precipitates" if no data exists.  
    4. **Validation**:  
    - Reject if:  
        - Image formats deviate from "Fig. X".  
        - Numerical values lack units.  
        - Any field is missing or renamed.  

    ### **Output**  
    ONLY the raw JSON array as shown above, with no extra text, markdown, or comments.  
    """

    pt_structure4="""INPUT: 
    "sample_info": <{samples}>

    INSTRUCTION:
    Convert "sample_info" into a **strictly formatted JSON array** following the exact schema and rules below. Output **ONLY the raw JSON** without any additional text or explanations.  

    ### **Required JSON Structure** 
    [{{
        "sample_id": extracted from "sample_info", 
        "other_process": extracted from "sample_info", 
        "thermal_process": 
        [{{
            "temperature": the temperature at which the sample is heated,
            "time":the duration of the heating process,
            "cooling method": the method used to cool the sample after heating, 
            "pressure": the pressure applied **DURING** the heating process, 
            "atmosphere": the gas or medium surrounding the sample during the heating process
            }}...]
    }},...]
    where:
        -"thermal process" of each sample should be listed respectivly. If a sample has multiple thermal process, please list them strictly in sequence; if a sample has no thermal process, please return [{{"sample_id":"xxx", "thermal_process": []}}...].

    Attention: 
    - If the original text is a range, keep the range
    - Even if multiple samples have the same parameters, do not omit them; list all of them.
    - If there is no precise value, fill in "NONE" directly. It is more acceptable to fill in "NONE" than to provide an incorrect value.
    """