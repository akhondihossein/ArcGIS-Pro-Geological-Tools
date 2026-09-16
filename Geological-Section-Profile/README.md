# Geological Section Profile

**ArcGIS Pro Python Toolbox for preparing geological section profiles from GIS and elevation data**

Geological Section Profile is a specialized ArcGIS Pro Python Toolbox tool designed to prepare the geometric components required for geological section construction.

The tool combines a Geological Section Line, DEM, lithological polygons, faults, and optional line or polygon features to create a structured set of outputs in an Elevation–Distance coordinate system.

It is intended to reduce repetitive GIS preparation work while keeping geological interpretation under the control of the user.

---

## Features

- Sample a DEM along a Geological Section Line.
- Create an Elevation–Distance topographic profile.
- Create a polygon base below the profile for section layout.
- Extract lithological boundary intersections.
- Create lithology boundary markers.
- Create lithology unit labels.
- Place lithology labels at the midpoint of the actual unit interval along the section.
- Extract Fault intersections with the section.
- Create Fault Intersection Markers.
- Support an optional Other Polygon Feature.
- Support an optional Other Line Feature.
- Store source names or IDs when corresponding Fields are selected.
- Reverse the section processing direction.
- Control marker height as a percentage of elevation range.
- Define section layout scale.
- Create GIS-ready Shapefile outputs.
- Create `.lyrx` layer files when available for styling and labeling.

---

## Intended Applications

Geological Section Profile can support:

- Geological mapping
- Structural geology
- Mining geology
- Mineral exploration
- Engineering geology
- Cross-section preparation
- Fault and lithology visualization
- Terrain profile extraction
- Preparation of GIS-based geological sections

The tool is particularly useful when several sections must be prepared using a consistent and repeatable GIS workflow.

---

## Input Data

### Lithology Polygon Layer

A Polygon layer representing geological units such as formations, members, deposits, or mapped rock units.

The tool intersects the Lithology polygons with the Geological Section Line and identifies section crossings with lithological boundaries.

### Lithology Name Field

An optional Field containing the name or code of each geological unit.

When selected, the Field is used for Lithology output attributes and for generating Lithology Labels.

### Fault Line Layer

A Polyline layer containing faults.

The tool calculates where each Fault intersects the Geological Section Line and records its position as Distance / Chainage and Elevation.

### Other Polygon Feature

An optional Polygon layer for additional features such as alteration zones, mining areas, geomorphological units, or other mapped areas.

### Other Line Feature

An optional Polyline layer for features such as rivers, roads, lineaments, structural boundaries, or other lines that should appear in the section preparation outputs.

### Geological Section Line

The Polyline defining the actual section path.

Its direction establishes the default Distance direction, and its length defines the horizontal Distance axis of the profile.

### DEM Raster

The Digital Elevation Model used to obtain ground-surface elevation along the section.

The DEM should cover the complete section path and should contain valid elevation values along the sampling route.

---

## Processing Workflow

The tool follows a structured sequence:

1. Validate input geometry types.
2. Read the Geological Section Line.
3. Reverse the section direction when requested.
4. Check the Coordinate System.
5. Sample the DEM along the section.
6. Convert samples into Elevation–Distance coordinates.
7. Create the Topographic Profile.
8. Create the TopoPoly layout polygon.
9. Identify Lithology intersections.
10. Identify Fault intersections.
11. Identify optional line and polygon intersections.
12. Calculate Distance / Chainage for each intersection.
13. Obtain elevation at each intersection.
14. Create Elevation–Distance markers.
15. Create Lithology Labels at unit midpoints when a Lithology Name Field is available.
16. Create `.lyrx` files when available.

---

## Elevation–Distance Coordinate System

The marker outputs are created specifically for section drawing.

- **X = Distance from the beginning of the section**
- **Y = Elevation**

These marker coordinates are therefore not the original geographic or projected map coordinates.

This behavior is intentional: the outputs are designed to be used in the construction and visualization of a geological section.

For accurate Distance calculations, a suitable **Projected Coordinate System** is recommended.

---

## Lithology Boundary Markers

When **Create Lithology Boundary Markers** is enabled, the tool identifies where the Geological Section Line crosses Lithology boundaries.

The resulting markers contain information such as:

- Marker type
- Lithology name or ID when available
- Distance / Chainage
- Elevation
- Source Object ID
- Original map coordinates when available

The actual boundary position is preserved.

---

## Lithology Labels

When a Lithology Name Field is selected, the tool can create a separate Lithology Label output.

Labels are not placed directly on the boundary between two units.

Instead, the tool identifies the actual section interval contained inside each Lithology Polygon and places the label at the midpoint of that interval.

For example:

```text
Unit interval: 120 → 460
Label position: approximately 290
```

The label elevation is taken from the topographic profile at the same Distance.

This provides a cleaner arrangement for geological section annotation.

---

## Fault Intersection Markers

When **Create Fault Intersection Markers** is enabled, the tool identifies Fault intersections with the Geological Section Line.

For each intersection, the tool calculates:

- Distance / Chainage
- Elevation
- Fault name or ID when available
- Source Object ID
- Original map coordinates when available

If a Fault and Lithology Boundary occur at the same Chainage, both markers are retained.

---

## Section Layout Scale

The **Section Layout Scale** parameter is entered as the scale denominator.

For example:

```text
10000 = 1:10,000
5000  = 1:5,000
25000 = 1:25,000
```

The tool uses the scale value to construct the layout polygon below the topographic profile.

The depth of this polygon is:

```text
TopoPoly depth = 0.04 × scale denominator
```

This is a layout geometry and should not be interpreted as true geological thickness or true subsurface depth.

---

## Marker Height

Marker height is controlled as a percentage of the profile elevation range.

```text
Marker Height =
Elevation Range × Percentage ÷ 100
```

For example, with an elevation range of 600 m and a Marker Height of 3.75%:

```text
600 × 3.75 ÷ 100 = 22.5 m
```

This parameter controls visual marker size only.

---

## Reverse Section Direction

Enable **Reverse Section Direction** when the section should be processed in the opposite direction.

When enabled:

- The section direction is reversed.
- Distance order is reversed.
- The order of geological markers along the section is updated accordingly.

This is useful when a project requires a consistent section orientation.

---

## Main Outputs

| Output | Geometry | Purpose |
|---|---|---|
| Topo | Polyline | Topographic Elevation–Distance profile |
| TopoPoly | Polygon | Layout polygon below the profile |
| Lith | Polyline | Lithology boundary markers |
| LithLabel | Point | Lithology unit label points |
| Fault | Polyline | Fault intersection markers |
| OtherP | Polyline | Optional Other Polygon markers |
| OtherL | Polyline | Optional Other Line markers |
| `.lyrx` | Layer file | Styling and labeling support when available |

---

## Important Output Fields

Depending on the output, fields may include:

- `ID` — internal feature identifier
- `TYPE` — marker type
- `NAME` — source Feature name or ID
- `M_DIST` — Distance / Chainage
- `M_ELEV` — elevation at marker position
- `MAP_X` — original intersection X coordinate
- `MAP_Y` — original intersection Y coordinate
- `SRC_OID` — source Object ID
- `ELEV_BOT` — lower elevation of the profile polygon when available

---

## Recommended Starting Settings

```text
Lithology Polygon Layer = geological unit layer
Lithology Name Field = LITHOLOGY
Fault Line Layer = fault layer
Geological Section Line = section line
DEM Raster = DEM covering the section
DEM Sampling Interval = 10 m
Section Layout Scale = 10000
Marker Height = 3.75%
Reverse Section Direction = False
Create Lithology Boundary Markers = True
Create Fault Intersection Markers = True
Output Base Name = Section
```

The Sampling Interval should be considered together with the DEM cell size.

---

## Installation

1. Download the Python Toolbox (`.pyt`).
2. Place it in a suitable folder.
3. Open **ArcGIS Pro**.
4. Open the **Catalog** pane.
5. Connect to the folder containing the toolbox.
6. Open the toolbox.
7. Double-click **Geological Section Profile**.
8. Select the required input layers.
9. Configure the parameters.
10. Select an Output Folder and Output Base Name.
11. Run the tool.

---

## Documentation

For complete parameter descriptions, processing logic, output fields, examples, troubleshooting, and practical recommendations, see:

- `Geological_Section_Profile_Complete_Help_Guide_EN.md`

---

## Quality and Coordinate System Recommendations

For reliable section preparation:

- Use a suitable Projected Coordinate System for accurate Distance calculations.
- Ensure the DEM covers the entire section.
- Check the section path for NoData values.
- Select a Sampling Interval consistent with DEM cell size.
- Verify the direction of the Geological Section Line.
- Use Reverse Section Direction when required.
- Select a Lithology Name Field when unit labels are needed.
- Use a separate Output Base Name for each section.

---

## Geological Interpretation

The tool prepares geometric information for a geological section; it does not automatically interpret subsurface geology.

The Topographic Profile represents the ground surface extracted from the DEM.

Lithology and Fault markers represent surface intersections with the section path. They do not independently define:

- True geological thickness
- Subsurface layer geometry
- Geological dip and strike
- Fault displacement
- Subsurface continuation of units

Final geological interpretation should incorporate available field observations, boreholes, structural measurements, and geological relationships.

---

## Quick Checklist

- [ ] Lithology Polygon Layer selected
- [ ] Lithology Name Field selected when needed
- [ ] Fault Line Layer selected
- [ ] Fault Name / ID Field selected when needed
- [ ] Geological Section Line is a valid Polyline
- [ ] DEM covers the entire section
- [ ] DEM Sampling Interval is greater than zero
- [ ] Section Layout Scale is appropriate
- [ ] Marker Height is positive
- [ ] Section direction checked
- [ ] Output Folder exists and is writable
- [ ] Output Base Name defined

---

## License

Add your preferred license here before public distribution.

## Author

**Hossein Akhondi**

