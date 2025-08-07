# How to Use pgf-umlcd for UML Class Diagrams in LaTeX

## Overview

**pgf-umlcd** is a LaTeX package for drawing UML Class Diagrams. It's built on top of the popular PGF/TikZ graphics package and provides convenient macros for creating professional UML diagrams.

**Author**: Yuan Xu (xuyuan.cn@gmail.com)  
**Version**: 0.3 (as of May 22, 2022)  
**License**: LaTeX Project Public License 1.3c / GNU General Public License v2

## Official Documentation & Links

- **CTAN Package Page**: https://ctan.org/pkg/pgf-umlcd
- **Official Manual (PDF)**: https://ctan.uib.no/graphics/pgf/contrib/pgf-umlcd/pgf-umlcd-manual.pdf
- **GitHub Repository**: https://github.com/xuyuan/pgf-umlcd
- **CTAN Archive**: https://ctan.org/tex-archive/graphics/pgf/contrib/pgf-umlcd
- **Stack Exchange Help**: https://tex.stackexchange.com/questions/tagged/pgf-umlcd

## Installation

### MiKTeX/TeX Live
```bash
# Check if already installed
texdoc pgf-umlcd

# If not available, install via package manager
# MiKTeX: Use MiKTeX Console to install pgf-umlcd
# TeX Live: Usually included, but can install with tlmgr
tlmgr install pgf-umlcd
```

### Manual Installation
1. Download from CTAN: https://ctan.org/tex-archive/graphics/pgf/contrib/pgf-umlcd
2. Place `pgf-umlcd.sty` in your LaTeX path or project directory

## Basic Usage

### Package Declaration
```latex
\usepackage{pgf-umlcd}
\usepackage{tikz}  % Required dependency

% Optional: Simplified mode (hides empty sections)
\usepackage[simplified]{pgf-umlcd}

% Optional: School mode (rounded corners for objects)
\usepackage[school]{pgf-umlcd}
```

### Basic Document Structure
```latex
\documentclass{article}
\usepackage{pgf-umlcd}
\usepackage{tikz}

\begin{document}
\begin{tikzpicture}
  % Your UML diagrams go here
\end{tikzpicture}
\end{document}
```

## Core Components

### 1. Classes

#### Basic Class
```latex
\begin{tikzpicture}
\begin{class}[text width=8cm]{ClassName}{0,0}
  \attribute{name : attribute type}
  \attribute{name : attribute type = default value}
  \operation{name(parameter list) : type of value returned}
  \operation[0]{virtualMethod(parameters) : return type}  % [0] = virtual
\end{class}
\end{tikzpicture}
```

#### Class with Visibility Modifiers
```latex
\begin{tikzpicture}
\begin{class}[text width=7cm]{BankAccount}{0,0}
  \attribute{+ owner : String}        % + = public
  \attribute{+ balance : Dollars}     % + = public
  \attribute{\# updateBalance : Dollars}  % # = protected
  \attribute{- privateField : String}     % - = private
  \attribute{$\sim$ packageField : String} % ~ = package
  \operation{+ deposit(amount : Dollars)}
  \operation{+ withdrawal(amount : Dollars)}
  \operation{\# updateBalance(newBalance : Dollars)}
\end{class}
\end{tikzpicture}
```

### 2. Abstract Classes
```latex
\begin{tikzpicture}
\begin{abstractclass}[text width=5cm]{BankAccount}{0,0}
  \attribute{owner : String}
  \attribute{balance : Dollars = 0}
  \operation{deposit(amount : Dollars)}
  \operation[0]{withdrawl(amount : Dollars)}  % Virtual method
\end{abstractclass}
\end{tikzpicture}
```

### 3. Interfaces
```latex
\begin{tikzpicture}
\begin{interface}{Person}{0,0}
  \attribute{firstName : String}
  \attribute{lastName : String}
  \operation[0]{getName() : String}
\end{interface}
\end{tikzpicture}
```

### 4. Objects (Instances)
```latex
\begin{tikzpicture}
\begin{object}[text width=6cm]{Instance Name}{0,0}
  \instanceOf{Class Name}
  \attribute{attribute name = value}
\end{object}
\end{tikzpicture}
```

#### Object with Methods (School Mode)
```latex
% First enable school mode
\switchUmlcdSchool

\begin{tikzpicture}
\begin{object}[text width=6cm]{Thomas' account}{0,0}
  \instanceOf{BankAccount}
  \attribute{owner = Thomas}
  \attribute{balance = 100}
  \operation{deposit(amount : Dollars)}
  \operation[0]{withdrawl(amount : Dollars)}
\end{object}
\end{tikzpicture}
```

## Relationships

### 1. Inheritance
```latex
\begin{tikzpicture}
\begin{class}[text width=5cm]{BankAccount}{0,0}
  \attribute{owner : String}
  \operation{deposit(amount : Dollars)}
\end{class}

\begin{class}[text width=7cm]{CheckingAccount}{-5,-5}
  \inherit{BankAccount}  % Inheritance relationship
  \attribute{insufficientFundsFee : Dollars}
  \operation{processCheck(checkToProcess : Check)}
\end{class}

\begin{class}[text width=7cm]{SavingsAccount}{5,-5}
  \inherit{BankAccount}  % Inheritance relationship
  \attribute{annualInteresRate : Percentage}
  \operation{depositMonthlyInterest()}
\end{class}
\end{tikzpicture}
```

### 2. Multiple Inheritance
```latex
\begin{tikzpicture}
\begin{class}[text width=2cm]{TArg}{0,0}
\end{class}
\begin{class}[text width=2cm]{TGroup}{5,0}
\end{class}
\begin{class}[text width=2cm]{TProgInit}{10,0}
\end{class}
\begin{class}[text width=2cm]{TProgram}{5,-2}
  \inherit{TProgInit}
  \inherit{TGroup}
  \inherit{TArg}
\end{class}
\end{tikzpicture}
```

### 3. Interface Implementation
```latex
\begin{tikzpicture}
\begin{interface}{Person}{0,0}
  \attribute{firstName : String}
  \attribute{lastName : String}
\end{interface}

\begin{class}{Professor}{-5,-5}
  \implement{Person}  % Interface implementation
  \attribute{salary : Dollars}
\end{class}

\begin{class}{Student}{5,-5}
  \implement{Person}  % Interface implementation
  \attribute{major : String}
\end{class}
\end{tikzpicture}
```

### 4. Association
```latex
\begin{tikzpicture}
\begin{class}[text width=7cm]{Flight}{0,0}
  \attribute{flightNumber : Integer}
  \attribute{departureTime : Date}
  \operation{delayFlight(numberOfMinutes : Minutes)}
\end{class}

\begin{class}{Plane}{11,0}
  \attribute{airPlaneType : String}
  \attribute{maximumSpeed : MPH}
  \attribute{tailID : String}
\end{class}

\association{Plane}{assignedPlane}{0..1}{Flight}{0..*}{assignedFlights}
\end{tikzpicture}
```

### 5. Unidirectional Association
```latex
\begin{tikzpicture}
\begin{class}[text width=6cm]{OverdrawnAccountsReport}{0,0}
  \attribute{generatedOn : Date}
  \operation{refresh()}
\end{class}

\begin{class}{BankAccount}{12,0}
  \attribute{owner : String}
  \attribute{balance : Dollars}
  \operation{deposit(amount : Dollars)}
\end{class}

\unidirectionalAssociation{OverdrawnAccountsReport}{overdrawnAccounts}{0..*}{BankAccount}
\end{tikzpicture}
```

### 6. Aggregation
```latex
\begin{tikzpicture}
\begin{class}{Car}{0,0}
\end{class}
\begin{class}{Wheel}{7.5,0}
\end{class}
\aggregation{Car}{wheels}{4}{Wheel}
\end{tikzpicture}
```

### 7. Composition
```latex
\begin{tikzpicture}
\begin{class}{Company}{0,0}
\end{class}
\begin{class}{Department}{10,0}
\end{class}
\composition{Company}{theDepartment}{1..*}{Department}
\end{tikzpicture}
```

## Packages

### Creating Packages
```latex
\begin{tikzpicture}
\begin{package}{Accounts}
  \begin{class}[text width=5cm]{BankAccount}{0,0}
    \attribute{owner : String}
    \attribute{balance : Dollars = 0}
    \operation{deposit(amount : Dollars)}
  \end{class}
  
  \begin{class}[text width=7cm]{CheckingAccount}{-5,-5}
    \inherit{BankAccount}
    \attribute{insufficientFundsFee : Dollars}
    \operation{processCheck(checkToProcess : Check)}
  \end{class}
\end{package}
\end{tikzpicture}
```

## Notes and Comments

### Adding Notes
```latex
\begin{tikzpicture}
\umlnote (note) {This is a note.};
\end{tikzpicture}
```

### Notes with Positioning
```latex
\begin{tikzpicture}
\begin{class}{MyClass}{0,0}
  \attribute{field : String}
\end{class}
\umlnote (note) at (3,1) {This explains the class};
\draw[dashed] (MyClass) -- (note);
\end{tikzpicture}
```

## Customization

### Color Customization
```latex
% Define custom colors
\renewcommand{\umltextcolor}{red}
\renewcommand{\umlfillcolor}{green}
\renewcommand{\umldrawcolor}{blue}

\begin{tikzpicture}
\begin{class}[text width=8cm]{ClassName}{0,0}
  \attribute{name : attribute type}
  \operation{name(parameter list) : type}
\end{class}
\end{tikzpicture}
```

### Individual Element Styling
```latex
% Style individual elements
\renewcommand{\umlfillcolor}{red}
\begin{class}{RedClass}{0,0}
  \attribute{field : String}
\end{class}

\renewcommand{\umlfillcolor}{blue}
\begin{class}{BlueClass}{5,0}
  \attribute{field : String}
\end{class}
```

## Advanced Features

### Custom Stereotypes
```latex
\begin{tikzpicture}
\begin{class}{<<stereotype>> ClassName}{0,0}
  \attribute{field : Type}
\end{class}
\end{tikzpicture}
```

### Complex Relationships with Custom Lines
```latex
\begin{tikzpicture}
\begin{class}{Factory}{0,0}
  \operation{createProduct()}
\end{class}
\begin{class}{Product}{5,-3}
\end{class}

% Custom dashed line with stereotype
\draw[umlcd style dashed line,->] (Factory) -- 
  node[above, sloped, black]{$<<$ instantiate $>>$} (Product);
\end{tikzpicture}
```

## Common Patterns

### Abstract Factory Pattern
```latex
\begin{tikzpicture}
\begin{interface}{AbstractFactory}{0,0}
  \operation[0]{+ CreateProductA()}
  \operation[0]{+ CreateProductB()}
\end{interface}

\begin{class}{ConcreteFactory1}{3,-4}
  \implement{AbstractFactory}
  \operation{+ CreateProductA()}
  \operation{+ CreateProductB()}
\end{class}

\begin{class}{ConcreteFactory2}{-3,-4}
  \implement{AbstractFactory}
  \operation{+ CreateProductA()}
  \operation{+ CreateProductB()}
\end{class}

\begin{interface}{AbstractProductA}{15,-2}
\end{interface}

\begin{class}{ProductA1}{12,-5}
  \implement{AbstractProductA}
\end{class}

\begin{class}{ProductA2}{18,-5}
  \implement{AbstractProductA}
\end{class}

% Custom instantiate relationships
\draw[umlcd style dashed line,->] (ConcreteFactory1) --
  node[above, sloped, black]{$<<$ instantiate $>>$} (ProductA1);
\draw[umlcd style dashed line,->] (ConcreteFactory2.south) ++ (1,0) -- 
  ++(0,-1) -- node[above, sloped, black]{$<<$ instantiate $>>$} 
  ++(20,0) -| (ProductA2);
\end{tikzpicture}
```

## Tips and Best Practices

### 1. Text Width Management
```latex
% Always specify text width for consistent appearance
\begin{class}[text width=6cm]{LongClassName}{0,0}
  \attribute{veryLongAttributeName : VeryLongTypeName}
\end{class}
```

### 2. Positioning
```latex
% Use coordinates for precise positioning
\begin{class}{ClassA}{0,0}
\end{class}
\begin{class}{ClassB}{5,-3}  % 5 units right, 3 units down
\end{class}
```

### 3. Grid for Layout Planning
```latex
\begin{tikzpicture}[show background grid]
% Enable grid for layout planning (remove in final version)
\begin{class}{MyClass}{0,0}
  \attribute{field : String}
\end{class}
\end{tikzpicture}
```

### 4. Debugging Underscore Issues
```latex
% If class names contain underscores, escape them or use alternatives
\begin{class}{My\_Class}{0,0}  % Escape underscore
\end{class}
% OR
\begin{class}{My Class}{0,0}   % Use space instead
\end{class}
```

## Troubleshooting

### Package Not Found
1. Check if pgf-umlcd is installed: `texdoc pgf-umlcd`
2. Install via package manager (MiKTeX Console or tlmgr)
3. Manual download from CTAN if needed

### Compilation Errors
1. Ensure TikZ is loaded: `\usepackage{tikz}`
2. Check for proper `tikzpicture` environment
3. Verify class/interface names don't contain special characters

### Layout Issues
1. Use `text width` parameter for consistent box sizes
2. Use `show background grid` option during development
3. Adjust coordinates systematically

## Related Packages

- **pgf-umlsd**: For UML sequence diagrams
- **tikz-uml**: Alternative UML package (more comprehensive but complex)
- **tikz-er**: For Entity-Relationship diagrams

## Community Resources

- **TeX Stack Exchange**: https://tex.stackexchange.com/questions/tagged/pgf-umlcd
- **CTAN Support**: Via package maintainers
- **GitHub Issues**: For bug reports and feature requests

---

*This guide is based on pgf-umlcd version 0.3 (May 2022) and the official documentation by Yuan Xu.*
