you are tasked to generalize the memory of a given role, here is the guildeline:

# Generalize Role Memory

- the role memory is given as a xml file with a specific structure, see the schema below.
- for each memory item, you need to determine if this is about this specific project, like speficic implementation details, bug fixes, etc, which is not suitable for generalization to other projects. If it is, then just remove it.
- for those memory items that are suitable for generalization, you need to extract the general knowledge from it, using placeholders for specific details related to this project, and make the content into general knowledge that can be applied to other projects.
- DO NOT modify the original file, create a new file and output it. If the file is not specified, then use the name `generalized-role-memory.xml`, put it into the same directory as the original file.

# Role Memory File Schema

Here is the schema for the role memory file, which defines the structure and constraints for storing declarative memory.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           elementFormDefault="qualified"
           targetNamespace="http://promptx.memory/schema"
           xmlns:tns="http://promptx.memory/schema">

  <!-- Root element definition -->
  <xs:element name="memory" type="tns:MemoryType">
    <xs:annotation>
      <xs:documentation>
        Root element for PromptX declarative memory storage.
        Contains a collection of memory items with structured content.
      </xs:documentation>
    </xs:annotation>
  </xs:element>

  <!-- Memory container type -->
  <xs:complexType name="MemoryType">
    <xs:annotation>
      <xs:documentation>
        Container for memory items. Each memory represents a structured
        knowledge unit with unique identification and temporal metadata.
      </xs:documentation>
    </xs:annotation>
    <xs:sequence>
      <xs:element name="item" type="tns:MemoryItemType" maxOccurs="unbounded">
        <xs:annotation>
          <xs:documentation>
            Individual memory item containing content and metadata.
          </xs:documentation>
        </xs:annotation>
      </xs:element>
    </xs:sequence>
  </xs:complexType>

  <!-- Memory item type -->
  <xs:complexType name="MemoryItemType">
    <xs:annotation>
      <xs:documentation>
        Individual memory item with unique identifier, timestamp, content, and tags.
        Represents a single unit of knowledge or experience.
      </xs:documentation>
    </xs:annotation>
    <xs:sequence>
      <xs:element name="content" type="tns:ContentType">
        <xs:annotation>
          <xs:documentation>
            Main content of the memory item. Contains structured text,
            code examples, technical documentation, or procedural knowledge.
          </xs:documentation>
        </xs:annotation>
      </xs:element>
      <xs:element name="tags" type="tns:TagsType">
        <xs:annotation>
          <xs:documentation>
            Categorization tags for the memory item. Used for
            semantic retrieval and content classification.
          </xs:documentation>
        </xs:annotation>
      </xs:element>
    </xs:sequence>
    
    <!-- Required attributes -->
    <xs:attribute name="id" type="tns:MemoryIdType" use="required">
      <xs:annotation>
        <xs:documentation>
          Unique identifier for the memory item. Format: mem_[timestamp]_[random_string]
          Example: mem_1753630020950_zg034mehy
        </xs:documentation>
      </xs:annotation>
    </xs:attribute>
    
    <xs:attribute name="time" type="tns:TimestampType" use="required">
      <xs:annotation>
        <xs:documentation>
          Human-readable timestamp when the memory was created.
          Format: YYYY/MM/DD HH:MM
          Example: 2025/07/27 23:27
        </xs:documentation>
      </xs:annotation>
    </xs:attribute>
  </xs:complexType>

  <!-- Content type for memory items -->
  <xs:complexType name="ContentType" mixed="true">
    <xs:annotation>
      <xs:documentation>
        Mixed content type allowing both text and embedded markup.
        Supports Markdown formatting, code blocks, and structured documentation.
      </xs:documentation>
    </xs:annotation>
    <xs:choice minOccurs="0" maxOccurs="unbounded">
      <xs:any processContents="skip"/>
    </xs:choice>
  </xs:complexType>

  <!-- Tags type -->
  <xs:simpleType name="TagsType">
    <xs:annotation>
      <xs:documentation>
        Space-separated or comma-separated list of tags for categorization.
        Tags help with semantic retrieval and content organization.
      </xs:documentation>
    </xs:annotation>
    <xs:restriction base="xs:string">
      <xs:pattern value="[#\w\s,\-_]*"/>
      <xs:maxLength value="500"/>
    </xs:restriction>
  </xs:simpleType>

  <!-- Memory ID type with specific pattern -->
  <xs:simpleType name="MemoryIdType">
    <xs:annotation>
      <xs:documentation>
        Unique memory identifier following the pattern: mem_[timestamp]_[random_string]
        Timestamp is Unix milliseconds, random string is alphanumeric.
      </xs:documentation>
    </xs:annotation>
    <xs:restriction base="xs:string">
      <xs:pattern value="mem_\d{13}_[a-z0-9]+"/>
      <xs:maxLength value="50"/>
    </xs:restriction>
  </xs:simpleType>

  <!-- Timestamp type -->
  <xs:simpleType name="TimestampType">
    <xs:annotation>
      <xs:documentation>
        Human-readable timestamp in format YYYY/MM/DD HH:MM
        Used for temporal organization and memory lifecycle management.
      </xs:documentation>
    </xs:annotation>
    <xs:restriction base="xs:string">
      <xs:pattern value="\d{4}/\d{2}/\d{2} \d{2}:\d{2}"/>
    </xs:restriction>
  </xs:simpleType>

  <!-- Additional constraints and annotations -->
  <xs:annotation>
    <xs:documentation>
      PromptX Declarative Memory Schema (DPML)
      
      This schema defines the structure for declarative memory storage in PromptX,
      a professional AI memory system. Memory items contain:
      
      1. Unique identification (id + timestamp)
      2. Structured content (mixed text/markup)
      3. Categorization tags for retrieval
      
      Key Features:
      - Temporal organization with dual timestamp formats
      - Mixed content supporting Markdown and code
      - Semantic tagging for intelligent retrieval
      - Unique identification for deduplication
      - Extensible content model
      
      Usage Context:
      - AI role-specific memory storage
      - Technical knowledge preservation
      - Experience and skill documentation
      - Cross-session memory persistence
      - Semantic search and retrieval
      
      Content Categories Observed:
      - Textual TUI development knowledge
      - PeiDocker project specifics
      - Testing methodologies and frameworks
      - Design patterns and best practices
      - Technical implementation details
      - Debugging and troubleshooting procedures
      - GUI design specifications
      - Screenshot capture techniques
      
      Version: 1.0
      Target: PromptX Memory System
      Created: 2025/07/28
    </xs:documentation>
  </xs:annotation>

</xs:schema>
```