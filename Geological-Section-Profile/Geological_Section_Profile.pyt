# ============================================================================
# PROTECTED TOOL METADATA
# ============================================================================
# Tool Name: Geological Section Profile
# Author / Creator: Eng. Hossein Akhondi
# Organization: Independent Geological GIS Development
# Contact Email: hossein.akhondi1988@gmail.com
# Creation Year: 2026
# Version: 1.0 (2026)
# Subject: Geological cross-section topographic profile and intersection markers
# Category: Geological GIS / Cross-Section Analysis / Terrain Profiling
# Platform: ArcGIS Pro / ArcPy Python Toolbox (.pyt)
#
# Description:
# This tool generates a topographic elevation profile along a geological section
# line from a DEM, creates geological intersection markers for lithology
# boundaries and faults, and can generate a scaled polygon beneath the profile
# for geological cross-section drafting. Marker and profile geometry are kept in
# Distance-Elevation coordinates while the output spatial-reference metadata is
# inherited from the Geological Section Line input.
#
# Keywords:
# ArcGIS Pro; ArcPy; Geological Section; Cross Section; Topographic Profile;
# DEM; Elevation Profile; Lithology; Fault; Geological Mapping; GIS; Geology;
# Distance-Elevation; Section Scale; Profile Polygon
#
# Rights / Attribution:
# Copyright (c) 2026 Eng. Hossein Akhondi. All rights reserved.
# Attribution must be retained in any redistributed or modified copy.
# Contact: hossein.akhondi1988@gmail.com
#
# Metadata Protection Notice:
# This metadata block is intentionally preserved as tool provenance. Do not
# remove, replace, or falsify the author, creation year, attribution, or contact
# information.
# ============================================================================

import re
# -*- coding: utf-8 -*-
import arcpy
import os
import math

class Toolbox(object):
    def __init__(self):
        self.label = "Geological Section Tools"
        self.alias = "geosection"
        self.tools = [GeologicalSectionMarkers]

class GeologicalSectionMarkers(object):
    def __init__(self):
        self.label = "Geological Section Profile"
        self.description = (
            "Creates GIS-ready Shapefile outputs for manual geological "
            "cross-section construction. The final cross-section is not "
            "drawn automatically."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        p = []

        lith = arcpy.Parameter(
            displayName="Lithology Polygon Layer",
            name="lithology", datatype="GPFeatureLayer",
            parameterType="Required", direction="Input")
        lith.filter.list = ["Polygon"]
        lith.category = "Lithology"
        p.append(lith)

        lith_field = arcpy.Parameter(
            displayName="Lithology Name Field (Optional)",
            name="lithology_field", datatype="Field",
            parameterType="Optional", direction="Input")
        lith_field.parameterDependencies = ["lithology"]
        lith_field.filter.list = ["String"]
        lith_field.category = "Lithology"
        p.append(lith_field)

        other_poly = arcpy.Parameter(
            displayName="Other Polygon Feature (Optional)",
            name="other_polygon", datatype="GPFeatureLayer",
            parameterType="Optional", direction="Input")
        other_poly.filter.list = ["Polygon"]
        other_poly.category = "Other Polygon Feature"
        p.append(other_poly)

        other_poly_field = arcpy.Parameter(
            displayName="Other Polygon Name Field (Optional)",
            name="other_polygon_field", datatype="Field",
            parameterType="Optional", direction="Input")
        other_poly_field.parameterDependencies = ["other_polygon"]
        other_poly_field.filter.list = ["String", "Integer", "SmallInteger"]
        other_poly_field.category = "Other Polygon Feature"
        p.append(other_poly_field)

        faults = arcpy.Parameter(
            displayName="Fault Line Layer",
            name="faults", datatype="GPFeatureLayer",
            parameterType="Required", direction="Input")
        faults.filter.list = ["Polyline"]
        faults.category = "Fault"
        p.append(faults)

        fault_field = arcpy.Parameter(
            displayName="Fault Name / ID Field (Optional)",
            name="fault_field", datatype="Field",
            parameterType="Optional", direction="Input")
        fault_field.parameterDependencies = ["faults"]
        fault_field.filter.list = ["String", "Integer", "SmallInteger"]
        fault_field.category = "Fault"
        p.append(fault_field)

        other_line = arcpy.Parameter(
            displayName="Other Line Feature (Optional)",
            name="other_line", datatype="GPFeatureLayer",
            parameterType="Optional", direction="Input")
        other_line.filter.list = ["Polyline"]
        other_line.category = "Other Line Feature"
        p.append(other_line)

        other_line_field = arcpy.Parameter(
            displayName="Other Line Name / ID Field (Optional)",
            name="other_line_field", datatype="Field",
            parameterType="Optional", direction="Input")
        other_line_field.parameterDependencies = ["other_line"]
        other_line_field.filter.list = ["String", "Integer", "SmallInteger"]
        other_line_field.category = "Other Line Feature"
        p.append(other_line_field)

        section = arcpy.Parameter(
            displayName="Geological Section Line",
            name="section", datatype="GPFeatureLayer",
            parameterType="Required", direction="Input")
        section.filter.list = ["Polyline"]
        section.category = "Section / DEM Settings"
        p.append(section)

        dem = arcpy.Parameter(
            displayName="DEM Raster",
            name="dem", datatype="GPRasterLayer",
            parameterType="Required", direction="Input")
        dem.category = "Section / DEM Settings"
        p.append(dem)

        interval = arcpy.Parameter(
            displayName="DEM Sampling Interval",
            name="sampling_interval", datatype="GPDouble",
            parameterType="Required", direction="Input")
        interval.value = 10.0
        interval.category = "Section / DEM Settings"
        p.append(interval)

        scale = arcpy.Parameter(
            displayName="Section Layout Scale (e.g. 10000 = 1:10,000)",
            name="section_scale", datatype="GPDouble",
            parameterType="Required", direction="Input")
        scale.value = 10000.0
        scale.category = "Section / DEM Settings"
        p.append(scale)

        marker_pct = arcpy.Parameter(
            displayName="Marker Height (% of Elevation Range)",
            name="marker_height_pct", datatype="GPDouble",
            parameterType="Required", direction="Input")
        marker_pct.value = 3.75
        marker_pct.category = "Section / DEM Settings"
        p.append(marker_pct)

        reverse = arcpy.Parameter(
            displayName="Reverse Section Direction",
            name="reverse_section", datatype="GPBoolean",
            parameterType="Required", direction="Input")
        reverse.value = False
        reverse.category = "Section / DEM Settings"
        p.append(reverse)

        show_lith = arcpy.Parameter(
            displayName="Create Lithology Boundary Markers",
            name="show_lithology", datatype="GPBoolean",
            parameterType="Required", direction="Input")
        show_lith.value = True
        show_lith.category = "Outputs / Marker Options"
        p.append(show_lith)

        show_fault = arcpy.Parameter(
            displayName="Create Fault Intersection Markers",
            name="show_faults", datatype="GPBoolean",
            parameterType="Required", direction="Input")
        show_fault.value = True
        show_fault.category = "Outputs / Marker Options"
        p.append(show_fault)

        out_folder = arcpy.Parameter(
            displayName="Output Folder",
            name="output_folder", datatype="DEFolder",
            parameterType="Required", direction="Input")
        p.append(out_folder)

        out_name = arcpy.Parameter(
            displayName="Output Base Name",
            name="output_name", datatype="GPString",
            parameterType="Required", direction="Input")
        out_name.value = "Section"
        p.append(out_name)

        return p

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        try:
            if parameters[10].value is not None and float(parameters[10].value) <= 0:
                parameters[10].setErrorMessage(
                    "Sampling interval must be greater than zero.")
            if parameters[11].value is not None:
                v = float(parameters[11].value)
                if v <= 0:
                    parameters[11].setErrorMessage(
                        "Section layout scale must be greater than zero.")
            if parameters[12].value is not None:
                v = float(parameters[12].value)
                if v <= 0:
                    parameters[12].setErrorMessage(
                        "Marker height percentage must be greater than zero.")
        except Exception:
            pass

    def _msg(self, messages, text):
        messages.addMessage(str(text))

    def _warn(self, messages, text):
        messages.addWarningMessage(str(text))

    def _clean_name(self, name):
        base = os.path.splitext(os.path.basename(name))[0]
        base = re.sub(r"[^A-Za-z0-9_]+", "_", base)
        base = base.strip("_") or "GeoSec"
        return base[:13]

    def _output_name(self, base, suffix):
        base_clean = re.sub(r"[^A-Za-z0-9]+", "_",
                            os.path.splitext(os.path.basename(base))[0]).strip("_")
        prefix = base_clean[:max(1, 13 - len(suffix) - 1)]
        return (prefix + "_" + suffix)[:13]

    def _section_geometry(self, fc, reverse):
        geoms = []
        with arcpy.da.SearchCursor(fc, ["SHAPE@"]) as cur:
            for (g,) in cur:
                if g is not None:
                    geoms.append(g)
        if not geoms:
            raise RuntimeError("Section line contains no valid geometry.")
        geom = geoms[0]
        for g in geoms[1:]:
            geom = geom.union(g)
        if geom.partCount > 1:
            parts = []
            for i in range(geom.partCount):
                part = geom.getPart(i)
                pts = [pt for pt in part if pt]
                if len(pts) >= 2:
                    parts.append(arcpy.Polyline(
                        arcpy.Array(pts), geom.spatialReference))
            if parts:
                geom = max(parts, key=lambda x: x.length)
        if reverse:
            geom = geom.reverse()
        return geom

    def _point_at(self, line, distance):
        if distance <= 0:
            return line.firstPoint
        if distance >= line.length:
            return line.lastPoint
        return line.positionAlongLine(distance, False).firstPoint

    def _project_point_to_dem(self, point, source_sr, dem_sr):
        """Project a map point to the DEM CRS without modifying source data."""
        if point is None:
            return None
        try:
            if (source_sr is None or dem_sr is None or
                    source_sr.factoryCode == dem_sr.factoryCode):
                return point
        except Exception:
            pass

        try:
            pg = arcpy.PointGeometry(point, source_sr, False, False)
            return pg.projectAs(dem_sr).firstPoint
        except Exception:
            return None

    def _dem_value(self, raster, point):
        """Fast bilinear DEM sampling with cached cell values.

        The previous implementation called GetCellValue four times for every
        profile point.  Here the same bilinear calculation is retained, but
        individual DEM cell values are cached, so each cell is queried only
        once during an execution.  This keeps the profile values unchanged
        while substantially reducing ArcPy geoprocessing overhead.
        """
        if point is None:
            return None
        try:
            x = float(point.X)
            y = float(point.Y)
            cell_x = float(raster.meanCellWidth)
            cell_y = float(raster.meanCellHeight)
            ext = raster.extent
            xmin = float(ext.XMin)
            ymin = float(ext.YMin)
            xmax = float(ext.XMax)
            ymax = float(ext.YMax)
            cols = int(raster.width)
            rows = int(raster.height)
            if cell_x <= 0 or cell_y <= 0 or cols <= 0 or rows <= 0:
                return None
            if x < xmin or x > xmax or y < ymin or y > ymax:
                return None

            # Initialize one small cache per DEM for this tool execution.
            cache_key = (str(getattr(raster, 'catalogPath', raster)),
                         xmin, ymin, cell_x, cell_y, cols, rows)
            if getattr(self, '_dem_cache_key', None) != cache_key:
                self._dem_cache_key = cache_key
                self._dem_cell_cache = {}

            fx = (x - xmin) / cell_x - 0.5
            fy = (y - ymin) / cell_y - 0.5
            ix = int(math.floor(fx))
            iy = int(math.floor(fy))
            tx = fx - ix
            ty = fy - iy

            if cols <= 1:
                ix = 0
                tx = 0.0
            elif ix < 0:
                ix = 0
                tx = 0.0
            elif ix >= cols - 1:
                ix = cols - 2
                tx = 1.0

            if rows <= 1:
                iy = 0
                ty = 0.0
            elif iy < 0:
                iy = 0
                ty = 0.0
            elif iy >= rows - 1:
                iy = rows - 2
                ty = 1.0

            def cell_value(col, row):
                key = (int(col), int(row))
                cache = self._dem_cell_cache
                if key in cache:
                    return cache[key]

                cx = xmin + (float(col) + 0.5) * cell_x
                cy = ymin + (float(row) + 0.5) * cell_y
                value = None
                try:
                    result = arcpy.management.GetCellValue(
                        raster, "{} {}".format(cx, cy))
                    text = str(result.getOutput(0)).strip()
                    if text and text.upper() not in ("NODATA", "NONE", "NAN"):
                        value = float(text)
                        if math.isnan(value):
                            value = None
                except Exception:
                    value = None
                cache[key] = value
                return value

            if cols <= 1 or rows <= 1:
                return cell_value(ix, iy)

            z00 = cell_value(ix, iy)
            z10 = cell_value(ix + 1, iy)
            z01 = cell_value(ix, iy + 1)
            z11 = cell_value(ix + 1, iy + 1)

            vals = (z00, z10, z01, z11)
            if all(v is not None for v in vals):
                z0 = z00 * (1.0 - tx) + z10 * tx
                z1 = z01 * (1.0 - tx) + z11 * tx
                return float(z0 * (1.0 - ty) + z1 * ty)

            candidates = (
                (z00, (1.0 - tx) * (1.0 - ty)),
                (z10, tx * (1.0 - ty)),
                (z01, (1.0 - tx) * ty),
                (z11, tx * ty),
            )
            weighted = [(z, w) for z, w in candidates
                        if z is not None and w > 0.0]
            if weighted:
                sw = sum(w for _, w in weighted)
                if sw > 0.0:
                    return float(sum(z * w for z, w in weighted) / sw)
            return None
        except Exception:
            return None

    def _name_for_oid(self, fc, oid_field, oid, field):
        if not field:
            return ""
        where = "{} = {}".format(
            arcpy.AddFieldDelimiters(fc, oid_field), int(oid))
        with arcpy.da.SearchCursor(fc, [field], where) as cur:
            for (v,) in cur:
                return "" if v is None else str(v)
        return ""

    def _intersections(self, section, fc, field, kind):
        """Find section intersections robustly.

        For polygon lithology, intersect the SECTION with the polygon
        BOUNDARY, not the polygon interior. This captures actual geological
        contacts even when the returned intersection is multipart/overlapping.
        """
        out = []
        desc = arcpy.Describe(fc)
        oid_field = desc.OIDFieldName
        is_polygon = desc.shapeType == "Polygon"

        with arcpy.da.SearchCursor(fc, ["OID@", "SHAPE@"]) as cur:
            for oid, geom in cur:
                if geom is None:
                    continue

                target = geom
                if is_polygon:
                    try:
                        target = geom.boundary()
                    except Exception:
                        target = None

                if target is None:
                    continue

                try:
                    inter = section.intersect(target, 1)
                except Exception:
                    continue

                if inter is None:
                    continue

                name = self._name_for_oid(fc, oid_field, oid, field)
                points = []

                def add_point(p):
                    if p is not None and hasattr(p, "X") and hasattr(p, "Y"):
                        points.append(arcpy.Point(float(p.X), float(p.Y)))

                try:
                    # Dimension=1 returns point/multipoint intersection output.
                    # Do not rely on Geometry.geometryType because that property
                    # is not exposed consistently in ArcGIS Pro Python.
                    if hasattr(inter, "firstPoint"):
                        add_point(inter.firstPoint)

                    if hasattr(inter, "partCount") and hasattr(inter, "getPart"):
                        for i in range(inter.partCount):
                            part = inter.getPart(i)
                            if part is None:
                                continue
                            try:
                                for p in part:
                                    if p is not None:
                                        add_point(p)
                            except TypeError:
                                add_point(part)
                except Exception:
                    pass

                # Remove exact/near-identical points produced by multipart
                # boundary intersections before returning records.
                seen = []
                for p in points:
                    duplicate = False
                    for q in seen:
                        if math.hypot(p.X - q.X, p.Y - q.Y) <= 1e-7:
                            duplicate = True
                            break
                    if not duplicate:
                        seen.append(p)

                for p in seen:
                    out.append({
                        "type": kind,
                        "name": name,
                        "point": p,
                        "source_oid": int(oid)
                    })

        return out

    def _dedupe(self, records, tolerance):
        records = sorted(records, key=lambda r: r["distance"])
        result = []
        for r in records:
            duplicate = False
            for old in result:
                if (r["type"] == old["type"] and
                        abs(r["distance"] - old["distance"]) <= tolerance):
                    duplicate = True
                    break
            if not duplicate:
                result.append(r)
        return result

    def _create_profile_line(self, folder, base, records, output_sr=None):
        """Create the topographic Distance-Elevation profile from DEM samples.

        ArcGIS-like approach: keep the sampled surface elevations and connect
        the densified Distance/Elevation samples directly. No Catmull-Rom,
        Bezier, or other artificial smoothing is applied.
        """
        name = self._output_name(base, "Topo")
        path = os.path.join(folder, name + ".shp")
        if arcpy.Exists(path):
            arcpy.management.Delete(path)

        if len(records) < 2:
            raise arcpy.ExecuteError(
                "At least two valid DEM samples are required to create the topographic profile.")

        clean = []
        for r in sorted(records, key=lambda q: float(q["distance"])):
            x = float(r["distance"])
            y = float(r["elevation"])
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            if clean and abs(x - clean[-1][0]) <= 1e-9:
                clean[-1] = (x, y)
            else:
                clean.append((x, y))

        if len(clean) < 2:
            raise arcpy.ExecuteError(
                "The DEM profile contains fewer than two unique valid samples.")

        arcpy.management.CreateFeatureclass(
            folder, name, "POLYLINE", spatial_reference=output_sr)
        with arcpy.da.InsertCursor(path, ["SHAPE@"]) as ic:
            ic.insertRow([arcpy.Polyline(arcpy.Array([
                arcpy.Point(x, y) for x, y in clean
            ]))])

        arcpy.management.AddField(path, "ID", "LONG")
        arcpy.management.AddField(path, "LENGTH_M", "DOUBLE")
        arcpy.management.AddField(path, "MIN_Z", "DOUBLE")
        arcpy.management.AddField(path, "MAX_Z", "DOUBLE")

        with arcpy.da.UpdateCursor(path, ["ID", "LENGTH_M", "MIN_Z", "MAX_Z"]) as uc:
            row = next(uc, None)
            if row is not None:
                row[0] = 1
                row[1] = float(clean[-1][0] - clean[0][0])
                row[2] = float(min(y for x, y in clean))
                row[3] = float(max(y for x, y in clean))
                uc.updateRow(row)

        return path

    def _create_profile_fill_polygon(self, folder, base, profile_curve, scale_denominator, output_sr=None):
        """Create the polygonal fill below the topographic profile.

        The requested vertical depth is exactly 4 cm on a 1:N layout scale,
        which corresponds to N * 0.04 metres in the profile's metre-based
        Distance/Elevation coordinate system.
        """
        if not profile_curve or len(profile_curve) < 2:
            raise arcpy.ExecuteError("At least two profile vertices are required to create the profile polygon.")

        scale_denominator = float(scale_denominator)
        if not math.isfinite(scale_denominator) or scale_denominator <= 0:
            raise arcpy.ExecuteError("Section layout scale must be greater than 0.")

        min_elev = min(float(y) for x, y in profile_curve)
        depth_m = scale_denominator * 0.04
        bottom_elev = min_elev - depth_m

        name = self._output_name(base, "TopoPoly")
        path = os.path.join(folder, name + ".shp")
        if arcpy.Exists(path):
            arcpy.management.Delete(path)

        arcpy.management.CreateFeatureclass(
            folder, name, "POLYGON", spatial_reference=output_sr)
        arcpy.management.AddField(path, "ID", "LONG")
        arcpy.management.AddField(path, "SCALE", "DOUBLE")
        arcpy.management.AddField(path, "DEPTH_M", "DOUBLE")
        arcpy.management.AddField(path, "MIN_ELEV", "DOUBLE")
        arcpy.management.AddField(path, "BOT_ELEV", "DOUBLE")

        # Follow the topographic profile in Distance/Elevation space, then
        # close it along a horizontal base at the requested depth.
        pts = [arcpy.Point(float(x), float(y)) for x, y in profile_curve]
        pts.append(arcpy.Point(float(profile_curve[-1][0]), bottom_elev))
        pts.append(arcpy.Point(float(profile_curve[0][0]), bottom_elev))
        pts.append(arcpy.Point(float(profile_curve[0][0]), float(profile_curve[0][1])))

        polygon = arcpy.Polygon(arcpy.Array(pts))
        with arcpy.da.InsertCursor(
                path, ["SHAPE@", "ID", "SCALE", "DEPTH_M", "MIN_ELEV", "BOT_ELEV"]) as ic:
            ic.insertRow([polygon, 1, scale_denominator, depth_m, min_elev, bottom_elev])

        return path, depth_m, min_elev, bottom_elev

    def _profile_curve(self, profile_fc):
        """Read profile vertices as sorted (distance, elevation) pairs."""
        pts = []
        with arcpy.da.SearchCursor(profile_fc, ["SHAPE@"]) as cur:
            for (geom,) in cur:
                if geom is None:
                    continue
                for part in geom:
                    if part is None:
                        continue
                    for p in part:
                        if p is not None:
                            pts.append((float(p.X), float(p.Y)))

        pts.sort(key=lambda v: v[0])
        cleaned = []
        for x, y in pts:
            if cleaned and abs(x - cleaned[-1][0]) <= 1e-9:
                # Keep the latest smoothed vertex at the same chainage.
                cleaned[-1] = (x, y)
            else:
                cleaned.append((x, y))
        return cleaned

    def _profile_elevation_at(self, curve, distance):
        """Linearly interpolate elevation from the final profile curve."""
        if not curve:
            return None
        x = float(distance)
        if x <= curve[0][0]:
            return curve[0][1]
        if x >= curve[-1][0]:
            return curve[-1][1]

        lo = 0
        hi = len(curve) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if curve[mid][0] <= x:
                lo = mid
            else:
                hi = mid

        x1, y1 = curve[lo]
        x2, y2 = curve[hi]
        if abs(x2 - x1) <= 1e-12:
            return y1
        f = (x - x1) / (x2 - x1)
        return y1 + f * (y2 - y1)

    def _create_marker_fc(self, folder, base, suffix, records, height,
                          offsets=None, profile_curve=None, output_sr=None):
        name = self._output_name(base, suffix)
        path = os.path.join(folder, name + ".shp")
        if arcpy.Exists(path):
            arcpy.management.Delete(path)

        arcpy.management.CreateFeatureclass(folder, name, "POLYLINE", spatial_reference=output_sr)
        for f, typ, ln in [
            ("ID", "LONG", None), ("TYPE", "TEXT", 20),
            ("NAME", "TEXT", 80), ("DIST_M", "DOUBLE", None),
            ("ELEV_M", "DOUBLE", None), ("X_MAP", "DOUBLE", None),
            ("Y_MAP", "DOUBLE", None), ("SRC_OID", "LONG", None)
        ]:
            if ln:
                arcpy.management.AddField(path, f, typ, field_length=ln)
            else:
                arcpy.management.AddField(path, f, typ)

        fields = ["SHAPE@", "ID", "TYPE", "NAME", "DIST_M", "ELEV_M",
                  "X_MAP", "Y_MAP", "SRC_OID"]

        with arcpy.da.InsertCursor(path, fields) as ic:
            for i, r in enumerate(records, 1):
                x = float(r["distance"])
                base_z = float(r["elevation"])
                if profile_curve:
                    z_interp = self._profile_elevation_at(profile_curve, x)
                    if z_interp is not None:
                        base_z = float(z_interp)

                offset = float(offsets.get(i - 1, 0.0)) if offsets else 0.0
                y = base_z + offset

                geom = arcpy.Polyline(arcpy.Array([
                    arcpy.Point(x, y),
                    arcpy.Point(x, y + height)
                ]))

                ic.insertRow([
                    geom, i, r["type"], r["name"], x,
                    base_z, r["point"].X, r["point"].Y,
                    r["source_oid"]
                ])
        return path

    def _create_lithology_label_fc(self, folder, base, lith_fc, lith_field, section, profile_curve, output_sr=None):
        """Create one label point inside each lithology interval along the section.

        Boundary markers remain exactly at lithology contacts.  Labels are
        placed at the midpoint of the portion of each lithology polygon
        crossed by the section, so the label identifies the unit between its
        boundary markers rather than sitting on a contact.
        """
        if not lith_fc or not arcpy.Exists(lith_fc):
            return None

        name = self._output_name(base, "LithLabel")
        path = os.path.join(folder, name + ".shp")
        if arcpy.Exists(path):
            arcpy.management.Delete(path)

        arcpy.management.CreateFeatureclass(
            folder, name, "POINT", spatial_reference=output_sr)
        for f, typ, ln in [
            ("ID", "LONG", None), ("TYPE", "TEXT", 20),
            ("NAME", "TEXT", 80), ("DIST_M", "DOUBLE", None),
            ("ELEV_M", "DOUBLE", None), ("X_MAP", "DOUBLE", None),
            ("Y_MAP", "DOUBLE", None), ("SRC_OID", "LONG", None)
        ]:
            if ln:
                arcpy.management.AddField(path, f, typ, field_length=ln)
            else:
                arcpy.management.AddField(path, f, typ)

        label_records = []
        oid_field = arcpy.Describe(lith_fc).OIDFieldName
        with arcpy.da.SearchCursor(lith_fc, ["OID@", "SHAPE@", lith_field]) as cur:
            for oid, geom, name_value in cur:
                if geom is None:
                    continue
                try:
                    inter = section.intersect(geom, 2)
                except Exception:
                    continue
                if inter is None:
                    continue

                segments = []
                try:
                    if hasattr(inter, "partCount") and hasattr(inter, "getPart"):
                        for i in range(inter.partCount):
                            part = inter.getPart(i)
                            pts = [pt for pt in part if pt is not None]
                            if len(pts) >= 2:
                                a = pts[0]
                                b = pts[-1]
                                da = float(section.measureOnLine(
                                    arcpy.PointGeometry(a, section.spatialReference, False, False), False))
                                db = float(section.measureOnLine(
                                    arcpy.PointGeometry(b, section.spatialReference, False, False), False))
                                if db < da:
                                    da, db = db, da
                                if db - da > 1e-9:
                                    segments.append((da, db))
                    elif hasattr(inter, "firstPoint") and hasattr(inter, "lastPoint"):
                        a = inter.firstPoint
                        b = inter.lastPoint
                        if a is not None and b is not None:
                            da = float(section.measureOnLine(
                                arcpy.PointGeometry(a, section.spatialReference, False, False), False))
                            db = float(section.measureOnLine(
                                arcpy.PointGeometry(b, section.spatialReference, False, False), False))
                            if db < da:
                                da, db = db, da
                            if db - da > 1e-9:
                                segments.append((da, db))
                except Exception:
                    segments = []

                for da, db in segments:
                    dmid = (da + db) * 0.5
                    pt = self._point_at(section, dmid)
                    elev = self._profile_elevation_at(profile_curve, dmid)
                    if pt is None or elev is None:
                        continue
                    label_records.append({
                        "distance": float(dmid),
                        "elevation": float(elev),
                        "point": pt,
                        "name": "" if name_value is None else str(name_value),
                        "source_oid": int(oid)
                    })

        label_records.sort(key=lambda r: r["distance"])
        with arcpy.da.InsertCursor(
                path, ["SHAPE@", "ID", "TYPE", "NAME", "DIST_M",
                       "ELEV_M", "X_MAP", "Y_MAP", "SRC_OID"]) as ic:
            for i, r in enumerate(label_records, 1):
                p = r["point"]
                geom = arcpy.PointGeometry(
                    arcpy.Point(float(r["distance"]), float(r["elevation"])),
                    output_sr)
                ic.insertRow([
                    geom, i, "LITH_LABEL", r["name"], r["distance"],
                    r["elevation"], p.X, p.Y, r["source_oid"]
                ])

        return path if label_records else None

    def _save_lithology_label_lyrx(self, label_fc, lyrx_path):
        """Save a label layer with NAME displayed as the lithology label."""
        if not label_fc or not arcpy.Exists(label_fc):
            return None
        tmp_name = "__gs_lith_label_{}".format(abs(hash(label_fc)) % 1000000)
        try:
            arcpy.management.MakeFeatureLayer(label_fc, tmp_name)
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            lyr = None
            for m in aprx.listMaps():
                for candidate in m.listLayers():
                    try:
                        if candidate.name == tmp_name:
                            lyr = candidate
                            break
                    except Exception:
                        pass
                if lyr:
                    break
            if lyr is None:
                return None

            try:
                lyr.showLabels = True
                classes = lyr.listLabelClasses()
                if classes:
                    classes[0].expression = "[NAME]"
                    classes[0].showClassLabels = True
            except Exception:
                pass

            arcpy.management.SaveToLayerFile(lyr, lyrx_path, "ABSOLUTE")
            return lyrx_path if os.path.exists(lyrx_path) else None
        except Exception:
            return None
        finally:
            try:
                arcpy.management.Delete(tmp_name)
            except Exception:
                pass

    def _create_separate_markers(self, folder, base, lith_records,
                                 fault_records, other_poly_records,
                                 other_line_records, height, profile_curve, output_sr=None):
        # Coincidence tolerance is based on chainage, not marker height.
        # This is deliberately generous enough to catch tiny geometric
        # differences between a lithology contact and a fault crossing.
        tol = max(0.5, min(5.0, float(self._marker_chainage_tolerance)))

        fault_d = [float(r["distance"]) for r in fault_records]
        lith_d = [float(r["distance"]) for r in lith_records]

        # Fault is the base marker. Lithology is ALWAYS stacked above a
        # coincident fault, while independent lithology markers remain on
        # the profile.
        fault_offsets = {i: 0.0 for i in range(len(fault_records))}
        lith_offsets = {}
        for i, r in enumerate(lith_records):
            d = float(r["distance"])
            same_fault = any(abs(d - fd) <= tol for fd in fault_d)
            lith_offsets[i] = float(height) if same_fault else 0.0

        other_poly_offsets = {}
        for i, r in enumerate(other_poly_records):
            d = float(r["distance"])
            stack = 0
            if any(abs(d - fd) <= tol for fd in fault_d):
                stack += 1
            if any(abs(d - ld) <= tol for ld in lith_d):
                stack += 1
            other_poly_offsets[i] = stack * float(height)

        other_poly_d = [float(r["distance"]) for r in other_poly_records]
        other_line_offsets = {}
        for i, r in enumerate(other_line_records):
            d = float(r["distance"])
            stack = 0
            if any(abs(d - fd) <= tol for fd in fault_d):
                stack += 1
            if any(abs(d - ld) <= tol for ld in lith_d):
                stack += 1
            if any(abs(d - od) <= tol for od in other_poly_d):
                stack += 1
            other_line_offsets[i] = stack * float(height)

        fault_fc = self._create_marker_fc(
            folder, base, "Fault", fault_records, height,
            fault_offsets, profile_curve, output_sr)

        lith_fc = self._create_marker_fc(
            folder, base, "Lith", lith_records, height,
            lith_offsets, profile_curve, output_sr)

        other_poly_fc = None
        if other_poly_records:
            other_poly_fc = self._create_marker_fc(
                folder, base, "OtherP", other_poly_records, height,
                other_poly_offsets, profile_curve, output_sr)

        other_line_fc = None
        if other_line_records:
            other_line_fc = self._create_marker_fc(
                folder, base, "OtherL", other_line_records, height,
                other_line_offsets, profile_curve, output_sr)

        return fault_fc, lith_fc, other_poly_fc, other_line_fc

    def _find_map_layer(self, input_path):
        try:
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            target = os.path.normcase(os.path.abspath(input_path))
            for m in aprx.listMaps():
                for lyr in m.listLayers():
                    try:
                        if not lyr.isFeatureLayer:
                            continue
                        ds = os.path.normcase(os.path.abspath(lyr.dataSource))
                        if ds == target:
                            return lyr
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    def _source_line_color(self, input_path, polygon=False):
        """Best-effort extraction of the displayed source color."""
        lyr = self._find_map_layer(input_path)
        if lyr is None:
            return None
        try:
            sym = lyr.symbology
            renderer = sym.renderer
            symbol = renderer.symbol
            if polygon:
                c = getattr(symbol, "outlineColor", None)
                if c is None:
                    c = getattr(symbol, "color", None)
            else:
                c = getattr(symbol, "color", None)
            return c
        except Exception:
            return None

    def _save_marker_lyrx(self, marker_fc, lyrx_path, color):
        """Save a colored .lyrx when ArcGIS Pro exposes source symbology."""
        if color is None:
            return None
        tmp_name = "__gs_marker_{}".format(abs(hash(marker_fc)) % 1000000)
        try:
            arcpy.management.MakeFeatureLayer(marker_fc, tmp_name)
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            lyr = None
            for m in aprx.listMaps():
                for candidate in m.listLayers():
                    try:
                        if candidate.name == tmp_name:
                            lyr = candidate
                            break
                    except Exception:
                        pass
                if lyr:
                    break

            if lyr is None:
                return None

            sym = lyr.symbology
            sym.updateRenderer("SimpleRenderer")
            sym.renderer.symbol.color = color
            lyr.symbology = sym
            arcpy.management.SaveToLayerFile(
                lyr, lyrx_path, "ABSOLUTE")
            return lyrx_path
        except Exception:
            return None
        finally:
            try:
                arcpy.management.Delete(tmp_name)
            except Exception:
                pass


    def execute(self, parameters, messages):
        lith = parameters[0].valueAsText
        lith_field = parameters[1].valueAsText or None
        other_polygon = parameters[2].valueAsText or None
        other_polygon_field = parameters[3].valueAsText or None
        faults = parameters[4].valueAsText
        fault_field = parameters[5].valueAsText or None
        other_line = parameters[6].valueAsText or None
        other_line_field = parameters[7].valueAsText or None
        section_fc = parameters[8].valueAsText
        dem_path = parameters[9].valueAsText
        interval = float(parameters[10].value)
        section_scale = float(parameters[11].value)
        marker_pct = float(parameters[12].value)
        reverse = bool(parameters[13].value)
        show_lith = bool(parameters[14].value)
        show_fault = bool(parameters[15].value)
        folder = parameters[16].valueAsText
        base = parameters[17].valueAsText

        arcpy.env.overwriteOutput = True

        if interval <= 0:
            raise arcpy.ExecuteError("Sampling interval must be > 0.")
        if section_scale <= 0:
            raise arcpy.ExecuteError("Section layout scale must be > 0.")
        if marker_pct <= 0:
            raise arcpy.ExecuteError("Marker height percentage must be > 0.")
        if not os.path.isdir(folder):
            raise arcpy.ExecuteError("Output folder does not exist.")

        def _shape_type(value, parameter_index):
            # GPFeatureLayer.valueAsText can be only the layer name (for example
            # "Fault") rather than a resolvable catalog path. Prefer the actual
            # parameter value object when available.
            param_value = parameters[parameter_index].value
            candidates = [param_value, value]
            last_error = None
            for candidate in candidates:
                if candidate is None:
                    continue
                try:
                    return arcpy.Describe(candidate).shapeType
                except Exception as exc:
                    last_error = exc
            raise arcpy.ExecuteError(
                "Could not access input layer '{}'. Details: {}".format(
                    value, last_error))

        for fc, expected, idx in [
            (lith, "Polygon", 0), (faults, "Polyline", 4),
            (section_fc, "Polyline", 8)
        ]:
            if _shape_type(fc, idx) != expected:
                raise arcpy.ExecuteError(
                    "Invalid geometry type for: {}".format(fc))

        if other_polygon:
            if _shape_type(other_polygon, 2) != "Polygon":
                raise arcpy.ExecuteError(
                    "Other Polygon Feature must be a Polygon layer.")
        if other_line:
            if _shape_type(other_line, 6) != "Polyline":
                raise arcpy.ExecuteError(
                    "Other Line Feature must be a Polyline layer.")

        section = self._section_geometry(section_fc, reverse)
        # CRS-only fix: use the input Geological Section Line CRS for every
        # output shapefile. Geometry/coordinates are otherwise unchanged.
        output_sr = section.spatialReference
        if section.length <= 0:
            raise arcpy.ExecuteError("Section line has zero length.")

        sr = section.spatialReference
        if sr and sr.type == "Geographic":
            self._warn(
                messages,
                "Section uses a Geographic CRS. A projected CRS is recommended "
                "for accurate distance calculations.")

        dem = arcpy.Raster(dem_path)
        dem_sr = dem.spatialReference

        self._msg(messages, "1/5 Sampling DEM elevations along section...")

        # Determine a controlled profile sampling step. This follows the same
        # principle as an elevation-profile workflow: densify the input line
        # before extracting surface elevations.
        try:
            cell = max(float(dem.meanCellWidth), float(dem.meanCellHeight))
        except Exception:
            cell = interval

        profile_step = max(float(interval), max(cell * 0.5, 1.0))

        distances = []
        d = 0.0
        while d < section.length:
            distances.append(d)
            d += profile_step
        if not distances or distances[-1] < section.length:
            distances.append(section.length)

        profile = []
        for d in distances:
            pt = self._point_at(section, d)
            sample_pt = self._project_point_to_dem(pt, sr, dem_sr)
            if sample_pt is None:
                continue
            z = self._dem_value(dem, sample_pt)
            if z is not None:
                profile.append({
                    "distance": float(d),
                    "elevation": float(z),
                    "x": float(pt.X),
                    "y": float(pt.Y)
                })

        if len(profile) < 2:
            raise arcpy.ExecuteError(
                "Fewer than two valid DEM samples were found along the section.")

        self._msg(messages, "2/5 Building smooth topographic profile...")

        # Save only the actual topographic profile; no profile point shapefile.
        profile_line_fc = self._create_profile_line(folder, base, profile, output_sr)
        profile_curve = self._profile_curve(profile_line_fc)

        topo_poly_fc, topo_depth_m, topo_min_elev, topo_bottom_elev = (
            self._create_profile_fill_polygon(
                folder, base, profile_curve, section_scale, output_sr)
        )
        self._msg(
            messages,
            "Profile polygon created: 4 cm at 1:{:.0f} = {:.3f} m below minimum elevation."
            .format(section_scale, topo_depth_m))

        # Store tolerance for the marker stacking routine.
        self._marker_chainage_tolerance = max(0.5, min(5.0, profile_step * 0.25))

        zmin = min(r["elevation"] for r in profile)
        zmax = max(r["elevation"] for r in profile)
        zrange = zmax - zmin
        marker_height = (
            zrange * marker_pct / 100.0
            if zrange > 0 else max(abs(zmax) * 0.01, 1.0)
        )

        lith_records = []
        fault_records = []
        other_poly_records = []
        other_line_records = []

        sources = []
        if show_lith:
            sources.append((lith, lith_field, "LITH_BOUND", "lith"))
        if show_fault:
            sources.append((faults, fault_field, "FAULT", "fault"))
        if other_polygon:
            sources.append(
                (other_polygon, other_polygon_field, "OTHER_POLY", "other_poly"))
        if other_line:
            sources.append(
                (other_line, other_line_field, "OTHER_LINE", "other_line"))

        processed_all = []

        self._msg(messages, "3/5 Finding geological intersections...")

        for fc, field, kind, bucket in sources:
            raw = self._intersections(section, fc, field, kind)
            processed = []

            for r in raw:
                p = arcpy.PointGeometry(r["point"], sr, False, False)
                try:
                    r["distance"] = float(section.measureOnLine(p, False))

                    sample_pt = self._project_point_to_dem(
                        r["point"], sr, dem_sr)
                    if sample_pt is None:
                        continue

                    z = self._dem_value(dem, sample_pt)
                    if z is None:
                        self._warn(
                            messages,
                            "Skipped {} at chainage {:.3f}: no DEM value."
                            .format(r["type"], r["distance"]))
                        continue

                    r["elevation"] = float(z)
                    processed.append(r)
                except Exception:
                    continue

            # Dedupe only inside each feature type. Fault + lithology at the
            # same chainage are intentionally retained as two markers.
            tolerance = max(0.01, min(0.5, profile_step * 0.02))
            processed = self._dedupe(processed, tolerance)

            if bucket == "lith":
                lith_records.extend(processed)
            elif bucket == "fault":
                fault_records.extend(processed)
            elif bucket == "other_poly":
                other_poly_records.extend(processed)
            elif bucket == "other_line":
                other_line_records.extend(processed)

            processed_all.extend(processed)

        self._msg(messages, "4/5 Creating profile markers...")

        fault_fc, lith_fc, other_poly_fc, other_line_fc = (
            self._create_separate_markers(
                folder, base, lith_records, fault_records,
                other_poly_records, other_line_records,
                marker_height, profile_curve, output_sr)
        )

        # Keep lithology boundary markers at the contacts, but place the
        # lithology NAME label at the midpoint of the actual unit interval.
        lith_label_fc = None
        lith_label_lyrx = None
        if show_lith and lith_field:
            lith_label_fc = self._create_lithology_label_fc(
                folder, base, lith, lith_field, section, profile_curve, output_sr)

        self._msg(messages, "5/5 Applying marker styles...")

        # Shapefiles do not store display colors. Create companion .lyrx files
        # when source symbology can be read from the current ArcGIS Pro map.
        lith_lyrx = None
        if lith_records:
            lith_lyrx = self._save_marker_lyrx(
                lith_fc,
                os.path.join(
                    folder, self._output_name(base, "Lith") + ".lyrx"),
                self._source_line_color(lith, polygon=True))

        if lith_label_fc:
            lith_label_lyrx = self._save_lithology_label_lyrx(
                lith_label_fc,
                os.path.join(
                    folder, self._output_name(base, "LithLabel") + ".lyrx"))

        fault_lyrx = None
        if fault_records:
            fault_lyrx = self._save_marker_lyrx(
                fault_fc,
                os.path.join(
                    folder, self._output_name(base, "Fault") + ".lyrx"),
                self._source_line_color(faults, polygon=False))

        other_poly_lyrx = None
        if other_poly_fc:
            other_poly_lyrx = self._save_marker_lyrx(
                other_poly_fc,
                os.path.join(
                    folder, self._output_name(base, "OtherP") + ".lyrx"),
                self._source_line_color(other_polygon, polygon=True))

        other_line_lyrx = None
        if other_line_fc:
            other_line_lyrx = self._save_marker_lyrx(
                other_line_fc,
                os.path.join(
                    folder, self._output_name(base, "OtherL") + ".lyrx"),
                self._source_line_color(other_line, polygon=False))

        self._msg(messages, "Geological Section Profile V12 completed.")
        self._msg(messages, "Topographic profile: {}".format(profile_line_fc))
        self._msg(messages, "Topographic profile polygon: {}".format(topo_poly_fc))
        self._msg(
            messages,
            "Scale 1:{:.0f}; polygon depth: {:.3f} m; minimum elevation: {:.3f}; bottom elevation: {:.3f}."
            .format(section_scale, topo_depth_m, topo_min_elev, topo_bottom_elev))
        self._msg(messages, "Lithology markers: {}".format(lith_fc))
        if lith_lyrx:
            self._msg(messages, "Lithology marker style: {}".format(lith_lyrx))
        if lith_label_fc:
            self._msg(messages, "Lithology labels: {}".format(lith_label_fc))
        if lith_label_lyrx:
            self._msg(messages, "Lithology label style: {}".format(lith_label_lyrx))
        self._msg(messages, "Fault markers: {}".format(fault_fc))
        if fault_lyrx:
            self._msg(messages, "Fault marker style: {}".format(fault_lyrx))

        if other_poly_fc:
            self._msg(
                messages, "Other polygon markers: {}".format(other_poly_fc))
            if other_poly_lyrx:
                self._msg(
                    messages,
                    "Other polygon marker style: {}".format(other_poly_lyrx))

        if other_line_fc:
            self._msg(
                messages, "Other line markers: {}".format(other_line_fc))
            if other_line_lyrx:
                self._msg(
                    messages,
                    "Other line marker style: {}".format(other_line_lyrx))

        self._msg(
            messages,
            "Total geological intersections: {}".format(len(processed_all)))
        self._msg(
            messages,
            "Marker height: {:.3f} (25% longer than the original default)."
            .format(marker_height))
        self._msg(
            messages,
            "Profile points and CSV output are disabled; only the final "
            "Distance-Elevation topographic profile and geological marker "
            "Shapefiles are created.")
        self._msg(
            messages,
            "Lithology contacts are extracted from polygon boundaries. "
            "At coincident chainage, lithology markers are stacked above "
            "fault markers. Final geological interpretation remains manual.")

