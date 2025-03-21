import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

def parse_ui_dump(xml_data: str) -> Dict[str, Any]:
    """
    Parse Android UI dump XML into a structured JSON format.
    
    Args:
        xml_data: The XML string from uiautomator dump
        
    Returns:
        A dictionary representation of the UI hierarchy
    """
    try:
        root = ET.fromstring(xml_data)
        return parse_node(root)
    except Exception as e:
        raise ValueError(f"Failed to parse UI dump: {str(e)}")

def parse_node(node: ET.Element) -> Dict[str, Any]:
    """
    Recursively parse an XML node into a dictionary.
    
    Args:
        node: An XML Element node
        
    Returns:
        A dictionary representation of the node
    """
    result = {}
    
    # Extract attributes
    for key, value in node.attrib.items():
        # Convert bounds string to coordinates
        if key == "bounds":
            bounds = parse_bounds(value)
            result["bounds"] = bounds
        else:
            result[key] = value
    
    # Extract children
    children = []
    for child in node:
        children.append(parse_node(child))
    
    if children:
        result["children"] = children
    
    return result

def parse_bounds(bounds_str: str) -> Dict[str, int]:
    """
    Parse the bounds string from Android UI dump.
    
    Format is typically: [left,top][right,bottom]
    
    Args:
        bounds_str: The bounds string from XML
        
    Returns:
        A dictionary with left, top, right, bottom coordinates
    """
    try:
        # Remove brackets and split by ][
        parts = bounds_str.replace("[", "").replace("]", "").split(",")
        
        if len(parts) >= 4:
            return {
                "left": int(parts[0]),
                "top": int(parts[1]),
                "right": int(parts[2]),
                "bottom": int(parts[3])
            }
        else:
            raise ValueError(f"Invalid bounds format: {bounds_str}")
    except Exception as e:
        raise ValueError(f"Failed to parse bounds '{bounds_str}': {str(e)}")

def get_element_center(bounds: Dict[str, int]) -> Dict[str, int]:
    """
    Calculate the center point of an element from its bounds.
    
    Args:
        bounds: Dictionary with left, top, right, bottom coordinates
        
    Returns:
        Dictionary with x, y coordinates
    """
    return {
        "x": (bounds["left"] + bounds["right"]) // 2,
        "y": (bounds["top"] + bounds["bottom"]) // 2
    }

def find_elements_by_text(ui_data: Dict[str, Any], text: str, exact_match: bool = False) -> List[Dict[str, Any]]:
    """
    Find UI elements by their text content.
    
    Args:
        ui_data: The parsed UI hierarchy
        text: The text to search for
        exact_match: Whether to require an exact match
        
    Returns:
        A list of matching elements
    """
    results = []
    _search_elements(ui_data, text, exact_match, results, "text")
    return results

def find_elements_by_resource_id(ui_data: Dict[str, Any], resource_id: str) -> List[Dict[str, Any]]:
    """
    Find UI elements by their resource ID.
    
    Args:
        ui_data: The parsed UI hierarchy
        resource_id: The resource ID to search for
        
    Returns:
        A list of matching elements
    """
    results = []
    _search_elements(ui_data, resource_id, True, results, "resource-id")
    return results

def _search_elements(node: Dict[str, Any], value: str, exact_match: bool, results: List[Dict[str, Any]], attr_name: str) -> None:
    """
    Recursively search for elements with matching attribute values.
    
    Args:
        node: Current node to search
        value: Value to match
        exact_match: Whether to require an exact match
        results: List to collect matching elements
        attr_name: Name of the attribute to match against
    """
    # Check if this node matches
    if attr_name in node:
        node_value = node[attr_name]
        if (exact_match and node_value == value) or (not exact_match and value.lower() in node_value.lower()):
            results.append(node)
    
    # Search children
    for child in node.get("children", []):
        _search_elements(child, value, exact_match, results, attr_name) 