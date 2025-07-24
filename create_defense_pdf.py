from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_defense_strategy_pdf():
    doc = SimpleDocTemplate("sample_docs/defense_strategy.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,  # Center
        spaceAfter=30,
    )
    
    story.append(Paragraph("AIRBORNE RECONNAISSANCE STRATEGY", title_style))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    # Introduction section
    story.append(Paragraph("Introduction", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    intro_text = """This document presents a strategy for developing a comprehensive, integrated and efficient airborne reconnaissance capability; one that, in concert with space-based assets, will meet the needs of the warfighter through 2010. It introduces the goal of extended reconnaissance—the ability to supply responsive and sustained intelligence data from anywhere within enemy territory, day or night, regardless of weather, as the needs of the warfighter dictate. This document is a top level description of the functions, system elements, and interfaces that comprise the future architecture for extended reconnaissance."""
    
    story.append(Paragraph(intro_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    objective_text = """This Objective Architecture is a blueprint for an interoperable system that will be flexible and scalable. It consists of a balanced mix of manned and unmanned platforms supported by an efficient global information infrastructure to minimize redundant data collection and expedite the delivery of reconnaissance data with particular emphasis on the direct connection between the sensors and the warfighters. To achieve this goal, the document presents a systematic approach for selecting, developing and deploying the specific airframes, sensors, communications, and information technologies that will be required to transition from the current capability to the Objective Architecture."""
    
    story.append(Paragraph(objective_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    vision_text = """The approach is built on a vision that addresses the realities of a changing global and fiscal environment and responds to Congress (emphasis added):</p>
    
    <p><i>"The committee, therefore, directs the Secretary of Defense, in coordination with the Director of Central Intelligence, to provide an integrated airborne reconnaissance strategy for the post-cold war era..."</i></p>
    
    <p>House Armed Services Committee<br/>30 July 1993"""
    
    story.append(Paragraph(vision_text, styles['Normal']))
    story.append(PageBreak())
    
    # Strategic Objectives
    story.append(Paragraph("Strategic Objectives", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    obj1_text = """<b>1. Extended Reconnaissance Capability</b><br/>
    The primary objective is to develop an extended reconnaissance capability that provides responsive and sustained intelligence data collection from any location within enemy territory, operating effectively day or night, in all weather conditions, as dictated by warfighter requirements."""
    
    story.append(Paragraph(obj1_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    obj2_text = """<b>2. Integrated Multi-Platform Architecture</b><br/>
    Establish a comprehensive system architecture that integrates manned and unmanned platforms with space-based assets, creating a synergistic reconnaissance network that maximizes operational effectiveness while minimizing redundancy."""
    
    story.append(Paragraph(obj2_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    obj3_text = """<b>3. Global Information Infrastructure</b><br/>
    Develop an efficient global information infrastructure that enables rapid data collection, processing, and dissemination to ensure timely delivery of actionable intelligence to warfighters in the field."""
    
    story.append(Paragraph(obj3_text, styles['Normal']))
    story.append(PageBreak())
    
    # System Architecture
    story.append(Paragraph("System Architecture", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    arch_text = """The Objective Architecture represents a fundamental shift from current reconnaissance capabilities to a future-oriented, integrated system design. This architecture is characterized by several key components:"""
    
    story.append(Paragraph(arch_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    comp1_text = """<b>Manned Platform Integration</b><br/>
    Traditional manned reconnaissance aircraft will continue to play a crucial role in the overall architecture, providing human judgment and adaptability in complex operational environments. These platforms will be enhanced with advanced sensor suites and communication systems to ensure seamless integration with unmanned systems."""
    
    story.append(Paragraph(comp1_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    comp2_text = """<b>Unmanned System Deployment</b><br/>
    Unmanned aerial vehicles (UAVs) will provide persistent surveillance capabilities, extended loiter times, and access to high-risk areas where manned platforms cannot safely operate. These systems will feature advanced autonomous capabilities and sophisticated sensor packages."""
    
    story.append(Paragraph(comp2_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    comp3_text = """<b>Space-Based Asset Coordination</b><br/>
    Satellite-based reconnaissance systems will provide global coverage and serve as a backbone for the integrated architecture, offering persistent monitoring capabilities and serving as communication relays for ground and airborne assets."""
    
    story.append(Paragraph(comp3_text, styles['Normal']))
    story.append(PageBreak())
    
    # Technical Requirements
    story.append(Paragraph("Technical Requirements", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    tech_intro = """The successful implementation of the extended reconnaissance capability requires adherence to specific technical requirements that ensure system interoperability, scalability, and operational effectiveness."""
    
    story.append(Paragraph(tech_intro, styles['Normal']))
    story.append(Spacer(1, 12))
    
    req1_text = """<b>Sensor Integration Standards</b><br/>
    All reconnaissance platforms must incorporate standardized sensor interfaces and data formats to ensure seamless information sharing across the integrated architecture. This includes common protocols for electro-optical, infrared, radar, and signals intelligence systems."""
    
    story.append(Paragraph(req1_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    req2_text = """<b>Communication Interoperability</b><br/>
    Robust, secure communication systems must enable real-time data transmission between all platform types and ground-based processing centers. This requires implementation of common communication protocols and encryption standards."""
    
    story.append(Paragraph(req2_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    req3_text = """<b>Data Processing Capabilities</b><br/>
    Advanced data processing and analysis capabilities must be distributed throughout the architecture to enable real-time intelligence production and reduce the burden on centralized processing facilities."""
    
    story.append(Paragraph(req3_text, styles['Normal']))
    story.append(PageBreak())
    
    # Implementation Strategy
    story.append(Paragraph("Implementation Strategy", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    impl_text = """The transition from current reconnaissance capabilities to the Objective Architecture requires a phased implementation approach that balances operational requirements with budgetary constraints and technological maturity."""
    
    story.append(Paragraph(impl_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    phase1_text = """<b>Phase 1: Foundation Development (Years 1-3)</b><br/>
    Establish core infrastructure components including communication networks, data processing centers, and initial platform modifications. Focus on developing interoperability standards and testing integration concepts."""
    
    story.append(Paragraph(phase1_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    phase2_text = """<b>Phase 2: Platform Integration (Years 4-7)</b><br/>
    Deploy enhanced manned platforms and initial unmanned systems. Integrate space-based assets into the operational architecture and conduct extensive testing of multi-platform coordination capabilities."""
    
    story.append(Paragraph(phase2_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    phase3_text = """<b>Phase 3: Full Capability Achievement (Years 8-10)</b><br/>
    Complete deployment of all system components and achieve full operational capability. Conduct comprehensive training programs and establish maintenance and logistics support structures."""
    
    story.append(Paragraph(phase3_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print("Defense strategy PDF created successfully!")

if __name__ == "__main__":
    create_defense_strategy_pdf()
