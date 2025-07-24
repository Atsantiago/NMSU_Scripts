# Prof-Tools for Maya

A comprehensive suite of instructor tools for grading and managing Maya assignments across NMSU's FDMA courses for the Creative Media Institute (CMI).

## 🎯 Overview

Prof-Tools provides an integrated menu-based interface in Maya that streamlines the grading process for 3D assignments. Built specifically for FDMA courses, this system combines automated analysis with interactive rubrics to ensure consistent, efficient, and fair grading.

## ✨ Key Features

### **🎯 Interactive Auto-Grader System**
- **5-Tier Performance Levels**: No, Low, Partial, High, Full Marks with predefined scoring ranges
- **Click-to-Score**: Interactive performance indicators set default scores instantly (0%, 65%, 75%, 95%, 100%)
- **Course-Specific Rubrics**: Tailored grading criteria for FDMA 1510 and FDMA 2530 assignments
- **Real-Time Calculations**: Automatic point calculation with manual override capability

### **📚 Assignment Management**
- **Dual Access Methods**: Direct menu navigation + organized assignment dialog
- **Course Organization**: FDMA 1510 and FDMA 2530 sections with expandable assignment lists
- **Custom Rubric Support**: Flexible template system for new assignment types
- **Batch Processing Ready**: Framework for future multi-student grading

### **🔧 Professional Workflow**
- **Maya Integration**: Seamless menu system integrated into Maya's interface
- **Empty File Detection**: Automatic detection and appropriate scoring for minimal submissions
- **Export Capabilities**: Professional grading reports with detailed feedback
- **Multi-Version Support**: Works across Maya 2020+ with persistent installation

### **⚡ Enhanced UI/UX**
- **Responsive Design**: Clean, organized interface optimized for grading workflows
- **Auto-Comments**: Context-aware feedback generation based on performance levels
- **Progress Tracking**: Visual indicators and real-time score updates
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## 📖 Installation

### Quick Install (Recommended)
1. **Download**: Get the latest release ZIP from [GitHub Releases](https://github.com/Atsantiago/NMSU_Scripts/releases)
2. **Extract**: Unzip to your desktop
3. **Install**: Drag `setup_drag_drop_maya_prof-tools.py` onto Maya's viewport
4. **Access**: Use the **Prof-Tools** menu in Maya's menu bar

### Manual Installation
```bash
# Clone repository
git clone https://github.com/Atsantiago/NMSU_Scripts.git

# Navigate to prof-tools
cd NMSU_Scripts/prof-tools

# Run installer
python setup_drag_drop_maya_prof-tools.py
```

## 🎓 Target Courses & Assignments

### **FDMA 1510 - Introduction to 3D Animation**
- *Assignment rubrics coming soon*
- Focus: Fundamental 3D modeling and animation projects

### **FDMA 2530 - Introduction to 3D Modeling**
- **U01_SS01 - Primitives**: Introduction to 3D modeling using primitive shapes
- *Additional assignments in development*
- Focus: Advanced modeling techniques and professional workflows

## 🚀 Usage

### Quick Start Grading
1. **Open Maya** with student assignment file
2. **Access Menu**: Prof-Tools → Grading Tools → Assignment Grading Rubric
3. **Select Course**: Choose FDMA 1510 or FDMA 2530 section
4. **Pick Assignment**: Click the appropriate assignment button
5. **Grade**: Use interactive performance indicators or manual percentage entry
6. **Export**: Generate professional grading report

### Direct Assignment Access
- **Prof-Tools Menu** → **Grading Tools** → **FDMA 2530** → **U01_L01_Primitives**

## 🏗️ Architecture

```
prof-tools/
├── prof/                           # Core Python package
│   ├── core/                      # Installation, versioning, system utilities
│   ├── ui/                        # Maya menu system and interface builders
│   ├── tools/                     # All grading functionality
│   │   ├── auto-grader/          # 🎯 Main grading system
│   │   │   └── assignments/      # Course-specific rubrics
│   │   │       ├── fdma1510/     # FDMA 1510 assignments
│   │   │       └── fdma2530/     # FDMA 2530 assignments
│   │   ├── core-tools/           # Maya workflow utilities
│   │   └── dev-tools/            # Development and maintenance tools
│   ├── utils/                    # Shared utility functions
│   └── tests/                    # Automated testing framework
└── setup_drag_drop_maya_prof-tools.py  # Drag-and-drop installer
```

## 📊 Current Status

**Version**: 0.3.5 (Stable Release)  
**Development Phase**: Active Development  
**Test Coverage**: Core functionality tested  
**Maya Compatibility**: 2020+ (Python 3.x)

### Recent Updates (v0.3.5)
- ✅ Interactive performance indicators with click-to-score functionality
- ✅ Fixed KeyError bugs in scoring system
- ✅ Enhanced grading workflow efficiency
- ✅ Multi-Maya version persistence resolution
- ✅ Course-organized assignment structure

### Development Roadmap
- 🔄 Additional FDMA 1510 and 2530 assignments
- 🔄 Batch grading capabilities for multiple students
- 🔄 LMS integration (Canvas/Blackboard export)
- 🔄 Advanced analytics and grade distribution analysis
- 🔄 Automated scene analysis and technical validation

## 🔧 System Requirements

- **Maya Version**: 2020+ (Python 3.x compatible)
- **Operating Systems**: Windows, macOS, Linux
- **Python**: 3.x (included with Maya 2020+)
- **Memory**: 4GB+ RAM recommended for large scenes
- **Storage**: 50MB for full installation

## 🛠️ Troubleshooting

### Common Issues

**Installation Problems**:
- Ensure Maya is closed before installation
- Check that you have write permissions to Maya's scripts directory
- Try running Maya as administrator if needed

**Maya Persistence Issues**:
- Fixed in v0.3.1 with multi-version userSetup.mel approach
- Tools automatically persist across Maya sessions

**Import Errors**:
- Check that prof-tools is installed in Maya's Python path
- Verify Maya version compatibility (2020+)

### Getting Help
- **Documentation**: [GitHub Wiki](https://github.com/Atsantiago/NMSU_Scripts/wiki)
- **Issues**: [Report Problems](https://github.com/Atsantiago/NMSU_Scripts/issues)
- **Contact**: [Alexander Santiago](https://github.com/Atsantiago)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- **Creative Media Institute** at New Mexico State University
- **FDMA Faculty and Students** for feedback and testing
- **Maya Community** for development resources and best practices

## 👨‍💻 Author

**Alexander T. Santiago**  
Creative Media Institute, New Mexico State University  
GitHub: [@Atsantiago](https://github.com/Atsantiago)

---

> *Designed by educators, for educators - streamlining the grading process while maintaining academic rigor and providing meaningful feedback to students.*