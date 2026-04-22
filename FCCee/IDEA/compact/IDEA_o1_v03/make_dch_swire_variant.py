#!/usr/bin/env python3
"""
make_dch_swire_variant.py

Generate an IDEA DCH sense-wire variant by producing 3 files:

  1) materials_<tag>.xml
     - copies the base materials file
     - ensures NiP alloy material exists (optional)
     - appends a new DCH_SWireMat... composite for the requested core + Ni(P) + Au stack

  2) DriftChamber_<tag>.xml
     - copies the base DriftChamber xml
     - updates:
         * the sense-wire thickness constant (supports CF and non-CF base files)
         * <wires ... SWire_material="..."> to the new material name

  3) IDEA_<tag>.xml
     - copies the base IDEA compact xml
     - updates includes:
         * materials include -> materials_<tag>.xml
         * drift chamber include -> DriftChamber_<tag>.xml
         * optionally rewrites shared refs either relatively or as absolute file: URIs

Convention used by this script
------------------------------
All coating thickness inputs are interpreted as TOTAL DIAMETER ADDED by that coating,
NOT radial thickness.

Examples:
  - 25 um CF core + 3.5 um Au means:
      total diameter = 28.5 um
      Au radial thickness = 1.75 um

  - 20 um W core + 0.3 um Au means:
      total diameter = 20.3 um
      Au radial thickness = 0.15 um

  - 25 um CF core + 0.2 um NiP + 1.2 um Au means:
      total diameter = 26.4 um
      NiP radial thickness = 0.1 um
      Au radial thickness  = 0.6 um

Mixture model
-------------
We generate a homogeneous "effective" material using cylindrical layer areas:
  A_core = pi*r0^2
  A_nip  = pi*(r1^2 - r0^2)
  A_au   = pi*(r2^2 - r1^2)

where:
  r0 = core_d_um / 2
  r1 = r0 + t_nip_um / 2
  r2 = r1 + t_au_um / 2

Effective density:
  rho_eff = (sum_i A_i * rho_i) / (sum_i A_i)

Mass fractions (DD4hep <fraction n="..."> is by mass):
  f_i = (A_i * rho_i) / (sum_j A_j * rho_j)

Shared reference handling
-------------------------
Generated variant bundles often live under:
  IDEA_o1_v03/variants/<tag>/

while shared files like:
  elements_o1_v01.xml
  DectDimensions_IDEA_o1_v03.xml

remain in the base IDEA_o1_v03 directory.

Use:
  --shared-ref-mode relative
or:
  --shared-ref-mode absolute --shared-base-dir /path/to/IDEA_o1_v03

to make the generated IDEA_<tag>.xml usable as-is from the variant directory.

Examples
--------
CF variant:
  python3 make_dch_swire_variant.py \
    --base_materials /path/to/materials_o1_v03.xml \
    --base_idea /path/to/IDEA_o1_v03CF.xml \
    --base_dch /path/to/DriftChamber_o1_v02CF.xml \
    --outdir /path/to/variants/CF25_Au3p5 \
    --tag 25CF_Au3p5 \
    --core-ref CFWire \
    --core-label CF \
    --core-d_um 25 \
    --t_nip_um 0 \
    --t_au_um 3.5 \
    --rho-core 2.0 \
    --shared-ref-mode absolute \
    --shared-base-dir /path/to/IDEA_o1_v03

W variant:
  python3 make_dch_swire_variant.py \
    --base_materials /path/to/materials_o1_v03.xml \
    --base_idea /path/to/IDEA_o1_v03W.xml \
    --base_dch /path/to/DriftChamber_o1_v02.xml \
    --outdir /path/to/variants/W20_Au0p3_defaultlike \
    --tag 20W_Au0p3_defaultlike \
    --core-ref W \
    --core-label W \
    --core-d_um 20 \
    --t_nip_um 0 \
    --t_au_um 0.3 \
    --rho-core 19.25 \
    --shared-ref-mode absolute \
    --shared-base-dir /path/to/IDEA_o1_v03
"""

from __future__ import annotations

import argparse
import math
import os
import re
from pathlib import Path


# ----------------------------
# string helpers
# ----------------------------
def sanitize_token(text: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "", text)
    if not token:
        raise ValueError(f"Cannot sanitize empty token from '{text}'")
    return token


def fmt_um_token(value: float) -> str:
    """
    Format microns for clean file/material-name tokens.
    Example:
      25       -> 25
      0.5      -> 0p5
      2.027088 -> 2p027088
    """
    s = f"{value:.12g}"
    s = s.replace("-", "m").replace(".", "p")
    return s


# ----------------------------
# math helpers
# ----------------------------
def _areas_um2(core_d_um: float, t_nip_um: float, t_au_um: float):
    """
    Build cylindrical layer areas using the convention that t_nip_um and t_au_um
    are TOTAL DIAMETER ADDED by those coatings, not radial thicknesses.
    """
    if core_d_um <= 0:
        raise ValueError("core_d_um must be > 0")
    if t_nip_um < 0 or t_au_um < 0:
        raise ValueError("t_nip_um and t_au_um must be >= 0")

    r0 = 0.5 * core_d_um
    r1 = r0 + 0.5 * t_nip_um
    r2 = r1 + 0.5 * t_au_um

    A_core = math.pi * (r0 ** 2)
    A_nip = math.pi * (r1 ** 2 - r0 ** 2) if t_nip_um > 0 else 0.0
    A_au = math.pi * (r2 ** 2 - r1 ** 2) if t_au_um > 0 else 0.0

    return (A_core, A_nip, A_au, r0, r1, r2)


def effective_density_and_mass_fractions(
    core_d_um: float,
    t_nip_um: float,
    t_au_um: float,
    rho_core: float,
    rho_nip: float,
    rho_au: float,
):
    A_core, A_nip, A_au, _, _, _ = _areas_um2(core_d_um, t_nip_um, t_au_um)
    A_tot = A_core + A_nip + A_au
    if A_tot <= 0:
        raise ValueError("Total area is zero.")

    rho_eff = (A_core * rho_core + A_nip * rho_nip + A_au * rho_au) / A_tot

    m_core = A_core * rho_core
    m_nip = A_nip * rho_nip
    m_au = A_au * rho_au
    m_tot = m_core + m_nip + m_au
    if m_tot <= 0:
        raise ValueError("Total mass proxy is zero.")

    f_core = m_core / m_tot
    f_nip = m_nip / m_tot
    f_au = m_au / m_tot
    return rho_eff, f_core, f_nip, f_au


def total_diameter_um(core_d_um: float, t_nip_um: float, t_au_um: float) -> float:
    return core_d_um + t_nip_um + t_au_um


def total_diameter_mm(core_d_um: float, t_nip_um: float, t_au_um: float) -> float:
    return total_diameter_um(core_d_um, t_nip_um, t_au_um) * 1e-3


def radial_thickness_um(added_diameter_um: float) -> float:
    return 0.5 * added_diameter_um


# ----------------------------
# URI / path helpers
# ----------------------------
def path_to_file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def should_leave_ref_unchanged(ref: str, keep_local_refs: set[str]) -> bool:
    if ref in keep_local_refs:
        return True
    if (
        ref.startswith("/")
        or ref.startswith("${")
        or ref.startswith("file:")
        or ref.startswith("root:")
        or "://" in ref
    ):
        return True
    return False


# ----------------------------
# XML patch helpers
# ----------------------------
def patch_idea_compact(
    text: str,
    old_materials_ref: str,
    new_materials_ref: str,
    old_dch_ref: str,
    new_dch_ref: str,
    *,
    shared_ref_mode: str,
    shared_base_dir: Path | None,
    generated_outdir: Path,
) -> str:
    """
    Patch the IDEA compact XML for a generated variant.

    Behavior:
      - replace the materials include with the new generated local materials file
      - replace the DriftChamber include with the new generated local DCH file
      - rewrite other shared refs either:
          * relatively from generated_outdir back to shared_base_dir
          * or as absolute file: URIs rooted at shared_base_dir
    """
    keep_local_refs = {new_materials_ref, new_dch_ref}

    text2 = text.replace(
        f'<gdmlFile  ref="{old_materials_ref}"/>',
        f'<gdmlFile  ref="{new_materials_ref}"/>',
    )
    text3 = text2.replace(
        f'<include ref="{old_dch_ref}"/>',
        f'<include ref="{new_dch_ref}"/>',
    )

    ref_pattern = re.compile(r'(<(?:include|gdmlFile)\s+ref=")([^"]+)(".*?/?>)')

    def _rewrite_ref(match):
        prefix, ref, suffix = match.groups()

        if should_leave_ref_unchanged(ref, keep_local_refs):
            return f"{prefix}{ref}{suffix}"

        if shared_base_dir is None:
            raise RuntimeError("shared_base_dir is required when rewriting shared refs.")

        target_path = (shared_base_dir / ref).resolve()

        if shared_ref_mode == "absolute":
            new_ref = path_to_file_uri(target_path)
        elif shared_ref_mode == "relative":
            new_ref = os.path.relpath(target_path, start=generated_outdir)
        else:
            raise ValueError(f"Unknown shared_ref_mode: {shared_ref_mode}")

        return f"{prefix}{new_ref}{suffix}"

    return ref_pattern.sub(_rewrite_ref, text3)


def patch_driftchamber(text: str, new_thickness_mm: float, new_swire_material: str) -> str:
    """
    Patch the sense-wire thickness constant and SWire_material reference.

    Supports both CF-style and non-CF-style DCH base files by trying several
    known sense-wire thickness constant names.
    """
    constant_names = [
        "DCH_SWire_thicknessCF",
        "DCH_SWire_thickness",
        "DCH_SWireThickness",
    ]

    text2 = text
    n1 = 0
    matched_constant = None

    for const_name in constant_names:
        pat_const = re.compile(
            rf'(<constant\s+name="{re.escape(const_name)}"\s+value=")\s*[^"]*(")',
            re.MULTILINE,
        )
        repl_const = r'\g<1>%.12g*mm\g<2>' % new_thickness_mm
        candidate_text, n_candidate = pat_const.subn(repl_const, text2, count=1)
        if n_candidate == 1:
            text2 = candidate_text
            n1 = 1
            matched_constant = const_name
            break

    if n1 != 1:
        raise RuntimeError(
            "Failed to patch sense-wire thickness constant. "
            f"Tried names: {', '.join(constant_names)}"
        )

    pat_mat = re.compile(r'(SWire_material\s*=\s*")([^"]*)(")', re.MULTILINE)

    def _mat_repl(match):
        return match.group(1) + new_swire_material + match.group(3)

    text3, n2 = pat_mat.subn(_mat_repl, text2, count=1)
    if n2 != 1:
        raise RuntimeError(
            "Failed to patch SWire_material attribute "
            "(pattern not found or ambiguous)."
        )

    return text3


def ensure_nip_material_block(text: str, nip_name: str) -> str:
    if re.search(rf'<material\s+name="{re.escape(nip_name)}"\b', text):
        return text

    block = f"""

<!-- Auto-added: Electroless nickel-phosphorus underplate (example definition) -->
<material name="{nip_name}">
  <comment>Electroless Ni-P underplate (approx. 90 wt% Ni, 10 wt% P); rho ~ 7.8 g/cm3</comment>
  <D type="density" value="7.8" unit="g/cm3"/>
  <fraction n="0.90" ref="Ni"/>
  <fraction n="0.10" ref="P"/>
</material>
"""
    if "</materials>" not in text:
        raise RuntimeError("materials file does not contain </materials> closing tag.")
    return text.replace("</materials>", block + "\n</materials>")


def insert_new_swire_material(text: str, material_block: str) -> str:
    anchor = "<!-- FCCeeIDEA: end of material for the drift chamber -->"
    if anchor in text:
        return text.replace(anchor, material_block + "\n\n" + anchor)

    if "</materials>" not in text:
        raise RuntimeError("materials file does not contain </materials> closing tag.")
    return text.replace("</materials>", material_block + "\n</materials>")


# ----------------------------
# backward-compatibility helpers
# ----------------------------
def resolve_core_inputs(args):
    """
    Support both new generic core arguments and old CF-specific ones.
    """
    core_ref = args.core_ref if args.core_ref is not None else args.cf_ref
    core_label = args.core_label if args.core_label is not None else (
        args.cf_label if args.cf_label is not None else "CF"
    )
    core_d_um = args.core_d_um if args.core_d_um is not None else args.cf_d_um
    rho_core = args.rho_core if args.rho_core is not None else args.rho_cf

    if core_ref is None:
        core_ref = "CFWire"
    if core_label is None:
        core_label = "CF"
    if core_d_um is None:
        raise ValueError("You must provide --core-d_um (or legacy --cf_d_um).")
    if rho_core is None:
        rho_core = 2.0

    return core_ref, core_label, core_d_um, rho_core


# ----------------------------
# main
# ----------------------------
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--base_materials",
        required=True,
        help="Path to base materials XML (e.g. materials_o1_v03.xml)",
    )
    parser.add_argument(
        "--base_idea",
        required=True,
        help="Path to base IDEA compact XML (e.g. IDEA_o1_v03CF.xml or IDEA_o1_v03W.xml)",
    )
    parser.add_argument(
        "--base_dch",
        required=True,
        help="Path to base DCH XML (e.g. DriftChamber_o1_v02CF.xml or DriftChamber_o1_v02.xml)",
    )

    parser.add_argument(
        "--outdir",
        required=True,
        help="Output directory for the variant files",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Tag for filenames/material-name uniqueness",
    )

    # New generic core args
    parser.add_argument(
        "--core-ref",
        default=None,
        help="Core material reference name already present in materials XML (e.g. CFWire, W, Al)",
    )
    parser.add_argument(
        "--core-label",
        default=None,
        help="Short clean token for naming/comments (e.g. CF, W, Al, SS)",
    )
    parser.add_argument(
        "--core-d_um",
        type=float,
        default=None,
        help="Core diameter [um] (e.g. 25 for CF, 20 for W)",
    )
    parser.add_argument(
        "--rho-core",
        dest="rho_core",
        type=float,
        default=None,
        help="Core density [g/cm3] used for effective homogeneous material",
    )

    # Backward-compatible legacy CF args
    parser.add_argument(
        "--cf_ref",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--cf_label",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--cf_d_um",
        type=float,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--rho_cf",
        type=float,
        default=None,
        help=argparse.SUPPRESS,
    )

    # Coatings
    parser.add_argument(
        "--t_au_um",
        type=float,
        required=True,
        help="Au thickness [um] as TOTAL DIAMETER ADDED",
    )
    parser.add_argument(
        "--t_nip_um",
        type=float,
        default=0.0,
        help="Ni(P) thickness [um] as TOTAL DIAMETER ADDED",
    )

    parser.add_argument(
        "--au_ref",
        default="Au",
        help="Name of Au material reference (default: Au)",
    )
    parser.add_argument(
        "--nip_name",
        default="NiP_90Ni_10P",
        help="Name to use for NiP alloy material (default: NiP_90Ni_10P)",
    )
    parser.add_argument(
        "--rho_au",
        type=float,
        default=19.3,
        help="Au density [g/cm3] (default: 19.3)",
    )
    parser.add_argument(
        "--rho_nip",
        type=float,
        default=7.8,
        help="NiP density [g/cm3] (default: 7.8)",
    )

    parser.add_argument(
        "--swire_mat_prefix",
        default="DCH_SWireMat",
        help="Prefix for new sense-wire material name",
    )

    parser.add_argument(
        "--shared-ref-mode",
        choices=["relative", "absolute"],
        default="relative",
        help=(
            "How to rewrite unchanged shared refs in the generated IDEA XML. "
            "'relative' makes them relative to the generated outdir. "
            "'absolute' rewrites them as file: URIs under --shared-base-dir."
        ),
    )
    parser.add_argument(
        "--shared-base-dir",
        default=None,
        help=(
            "Base IDEA_o1_v03 directory containing unchanged shared XMLs "
            "(e.g. elements_o1_v01.xml, DectDimensions_IDEA_o1_v03.xml). "
            "If omitted, inferred from the parent directory of --base_idea."
        ),
    )

    args = parser.parse_args()

    core_ref, core_label, core_d_um, rho_core = resolve_core_inputs(args)
    core_label_token = sanitize_token(core_label)

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    base_materials_path = Path(args.base_materials).resolve()
    base_idea_path = Path(args.base_idea).resolve()
    base_dch_path = Path(args.base_dch).resolve()

    if args.shared_base_dir is not None:
        shared_base_dir = Path(args.shared_base_dir).resolve()
    else:
        shared_base_dir = base_idea_path.parent.resolve()

    new_materials_name = f"materials_{args.tag}.xml"
    new_dch_name = f"DriftChamber_{args.tag}.xml"
    new_idea_name = f"IDEA_{args.tag}.xml"

    # Generic, clean material name
    swire_mat_name = (
        f"{args.swire_mat_prefix}_"
        f"{core_label_token}_{fmt_um_token(core_d_um)}umCore_"
        f"{fmt_um_token(args.t_nip_um)}umNiP_"
        f"{fmt_um_token(args.t_au_um)}umAu"
    )

    rho_eff, f_core, f_nip, f_au = effective_density_and_mass_fractions(
        core_d_um=core_d_um,
        t_nip_um=args.t_nip_um,
        t_au_um=args.t_au_um,
        rho_core=rho_core,
        rho_nip=args.rho_nip,
        rho_au=args.rho_au,
    )

    d_total_um = total_diameter_um(core_d_um, args.t_nip_um, args.t_au_um)
    d_total_mm = total_diameter_mm(core_d_um, args.t_nip_um, args.t_au_um)
    t_nip_rad_um = radial_thickness_um(args.t_nip_um)
    t_au_rad_um = radial_thickness_um(args.t_au_um)

    comment_lines = [
        (
            f"Sense wire: {core_d_um:g} um {core_label} core + "
            f"{args.t_nip_um:g} um total added Ni(P) diameter + "
            f"{args.t_au_um:g} um total added Au diameter"
        ),
        (
            f"Core material ref: {core_ref}; "
            f"equivalent radial coating thicknesses: "
            f"Ni(P) {t_nip_rad_um:g} um, Au {t_au_rad_um:g} um"
        ),
        "Homogeneous effective material using cylindrical layer areas and mass fractions",
    ]
    comment_xml = "\n    ".join(f"<comment>{line}</comment>" for line in comment_lines)

    nip_fraction_line = (
        f'    <fraction n="{f_nip:.12g}" ref="{args.nip_name}"/>\n'
        if args.t_nip_um > 0
        else ""
    )

    material_block = f"""

  <!-- Auto-generated sense-wire variant ({args.tag}) -->
  <material name="{swire_mat_name}">
    {comment_xml}
    <D type="density" value="{rho_eff:.10g}" unit="g/cm3"/>
    <fraction n="{f_core:.12g}" ref="{core_ref}"/>
{nip_fraction_line}    <fraction n="{f_au:.12g}" ref="{args.au_ref}"/>
  </material>
"""

    base_mat_text = base_materials_path.read_text(encoding="utf-8")
    base_idea_text = base_idea_path.read_text(encoding="utf-8")
    base_dch_text = base_dch_path.read_text(encoding="utf-8")

    mat_text = base_mat_text
    if args.t_nip_um > 0:
        mat_text = ensure_nip_material_block(mat_text, args.nip_name)

    if re.search(rf'<material\s+name="{re.escape(swire_mat_name)}"\b', mat_text):
        raise RuntimeError(
            f"Material {swire_mat_name} already exists in output; choose a different --tag."
        )

    mat_text = insert_new_swire_material(mat_text, material_block)

    dch_text = patch_driftchamber(
        base_dch_text,
        new_thickness_mm=d_total_mm,
        new_swire_material=swire_mat_name,
    )

    mat_match = re.search(
        r'<gdmlFile\s+ref="([^"]*materials[^"]*\.xml)"\s*/>',
        base_idea_text,
    )
    old_materials_ref = mat_match.group(1) if mat_match else "materials_o1_v03.xml"

    dch_match = re.search(
        r'<include\s+ref="([^"]*DriftChamber[^"]*\.xml)"\s*/>',
        base_idea_text,
    )
    if not dch_match:
        raise RuntimeError("Could not find DriftChamber include in base IDEA xml.")
    old_dch_ref = dch_match.group(1)

    idea_text = patch_idea_compact(
        base_idea_text,
        old_materials_ref=old_materials_ref,
        new_materials_ref=new_materials_name,
        old_dch_ref=old_dch_ref,
        new_dch_ref=new_dch_name,
        shared_ref_mode=args.shared_ref_mode,
        shared_base_dir=shared_base_dir,
        generated_outdir=outdir,
    )

    (outdir / new_materials_name).write_text(mat_text, encoding="utf-8")
    (outdir / new_dch_name).write_text(dch_text, encoding="utf-8")
    (outdir / new_idea_name).write_text(idea_text, encoding="utf-8")

    print("=== Wrote DCH sense-wire variant ===")
    print(f"outdir: {outdir}")
    print(f"  {new_materials_name}")
    print(f"  {new_dch_name}")
    print(f"  {new_idea_name}")
    print("")
    print("Sense wire parameters:")
    print(f"  Core material ref:           {core_ref}")
    print(f"  Core label:                  {core_label}")
    print(f"  Core diameter:               {core_d_um:g} um")
    print(f"  Ni(P) added diameter:        {args.t_nip_um:g} um")
    print(f"  Au added diameter:           {args.t_au_um:g} um")
    print(f"  Ni(P) radial thickness:      {t_nip_rad_um:g} um")
    print(f"  Au radial thickness:         {t_au_rad_um:g} um")
    print(f"  Total diameter:              {d_total_um:.6g} um ({d_total_mm:.12g} mm)")
    print(f"  Effective density:           {rho_eff:.10g} g/cm3")
    print("  Mass fractions:")
    print(f"    {core_ref}: {f_core:.12g}")
    if args.t_nip_um > 0:
        print(f"    {args.nip_name}: {f_nip:.12g}")
    print(f"    {args.au_ref}: {f_au:.12g}")
    print(f"  New SWire material name:     {swire_mat_name}")
    print("")
    print("Convention used:")
    print("  Coating inputs are interpreted as TOTAL DIAMETER ADDED, not radial thickness.")
    print("")
    print("Shared ref handling:")
    print(f"  shared_ref_mode:             {args.shared_ref_mode}")
    print(f"  shared_base_dir:             {shared_base_dir}")
    if args.shared_ref_mode == "absolute":
        print("  Unchanged shared refs are rewritten as absolute file: URIs.")
    else:
        print("  Unchanged shared refs are rewritten relative to the generated outdir.")
    print("")
    print("Run with:")
    print(f"  ddsim --compactFile {outdir / new_idea_name} ...")


if __name__ == "__main__":
    main()