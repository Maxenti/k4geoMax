#!/usr/bin/env python3

"""
wire_conductivity_match.py

Solve for the required outer coating thickness (interpreted as TOTAL ADDED DIAMETER)
needed to match the axial conductance per unit length of a reference wire.

This is intended for drift-chamber wire design studies where you want to compare
a new layered wire design against a reference wire such as:

  20 um W core + 0.3 um total added Au diameter

and ask, for example:

  "For a 25 um CF core with 0.5 um total added Ni diameter, how much total added
   Au diameter is needed to match the axial conductance of the default W+Au wire?"

Convention
----------
All layer thickness inputs are interpreted as TOTAL ADDED DIAMETER, not radial thickness.

Example:
  core diameter = 25 um
  intermediate layer nickel:0.5
means:
  - core diameter = 25.0 um
  - nickel adds 0.5 um to total diameter
  - nickel radial thickness = 0.25 um

Conductance model

-----------------

Example:


python3 wire_conductivity_match.py  \
    --core-material cf   \
    --core-d-um 40   \
    --intermediate-layer nickel:0.1   \
    --final-coating-material gold   \
    --sigma-override cf=4.62e6




-----------------
Axial conductance per unit length is modeled as:

  G' = sum_i sigma_i * A_i

for concentric cylindrical layers.

Units:
  - diameters in um
  - conductivity in S/m
  - areas in m^2
  - G' in S·m

Notes
-----
- For CF, conductivity is highly variable and anisotropic in reality.
  The built-in default is only a modeling assumption and should be overridden
  if you have a better measured value for your specific fiber/coating system.
- This script solves the electrical matching problem only.
  It does not optimize for mechanical strength, surface quality, aging,
  avalanche behavior, or manufacturability.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import List, Tuple


# ----------------------------------------------------------------------
# Built-in material library
# Conductivity values are engineering defaults for axial DC conductivity.
# CF is especially uncertain; override if you have a better number.
# ----------------------------------------------------------------------
MATERIALS = {
    "cf": {
        "label": "Carbon fiber (effective axial default)",
        "sigma_s_per_m": 1.0e5,
    },
    "tungsten": {
        "label": "Tungsten",
        "sigma_s_per_m": 1.79e7,
    },
    "aluminum": {
        "label": "Aluminum",
        "sigma_s_per_m": 3.50e7,
    },
    "stainless_steel": {
        "label": "Stainless steel",
        "sigma_s_per_m": 1.45e6,
    },
    "gold": {
        "label": "Gold",
        "sigma_s_per_m": 4.10e7,
    },
    "silver": {
        "label": "Silver",
        "sigma_s_per_m": 6.30e7,
    },
    "nickel": {
        "label": "Nickel",
        "sigma_s_per_m": 1.43e7,
    },
    "copper": {
        "label": "Copper",
        "sigma_s_per_m": 5.96e7,
    },
}


@dataclass
class Layer:
    material: str
    added_diameter_um: float  # total added diameter for this layer


def material_sigma(material: str, overrides: dict[str, float]) -> float:
    key = material.lower()
    if key in overrides:
        return overrides[key]
    if key not in MATERIALS:
        raise KeyError(
            f"Unknown material '{material}'. "
            f"Known materials: {', '.join(sorted(MATERIALS.keys()))}"
        )
    return MATERIALS[key]["sigma_s_per_m"]


def parse_sigma_override(items: List[str]) -> dict[str, float]:
    """
    Parse strings like:
      cf=2.5e5
      nickel=1.2e7
    """
    overrides: dict[str, float] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(
                f"Bad --sigma-override entry '{item}'. Expected material=value."
            )
        name, value = item.split("=", 1)
        name = name.strip().lower()
        overrides[name] = float(value.strip())
    return overrides


def parse_layer_list(items: List[str]) -> List[Layer]:
    """
    Parse strings like:
      nickel:0.5
      copper:0.2
    where thickness is TOTAL ADDED DIAMETER in um.
    """
    layers: List[Layer] = []
    for item in items:
        if ":" not in item:
            raise ValueError(
                f"Bad layer specification '{item}'. Expected material:added_diameter_um"
            )
        mat, val = item.split(":", 1)
        mat = mat.strip().lower()
        added = float(val.strip())
        if added < 0:
            raise ValueError(f"Layer added diameter must be >= 0, got {added}")
        layers.append(Layer(material=mat, added_diameter_um=added))
    return layers


def circular_area_from_diameter_um(d_um: float) -> float:
    """
    Cross-sectional area in m^2 for a circle of diameter d_um.
    """
    r_m = 0.5 * d_um * 1e-6
    return math.pi * r_m * r_m


def layered_conductance_per_length(
    core_material: str,
    core_diameter_um: float,
    layers: List[Layer],
    sigma_overrides: dict[str, float],
) -> Tuple[float, List[dict]]:
    """
    Compute axial conductance per unit length:
      G' = sum_i sigma_i * A_i
    for a concentric layered wire.

    Each layer thickness is TOTAL ADDED DIAMETER.
    """
    if core_diameter_um <= 0:
        raise ValueError("Core diameter must be > 0")

    details = []

    sigma_core = material_sigma(core_material, sigma_overrides)

    prev_d_um = core_diameter_um
    prev_area = circular_area_from_diameter_um(prev_d_um)

    Gprime = sigma_core * prev_area
    details.append({
        "kind": "core",
        "material": core_material,
        "diameter_um": core_diameter_um,
        "shell_added_diameter_um": 0.0,
        "area_m2": prev_area,
        "sigma_s_per_m": sigma_core,
        "sigmaA": sigma_core * prev_area,
    })

    running_d_um = core_diameter_um

    for layer in layers:
        if layer.added_diameter_um < 0:
            raise ValueError("Layer added diameter must be >= 0")

        running_d_um += layer.added_diameter_um
        new_area = circular_area_from_diameter_um(running_d_um)
        shell_area = new_area - prev_area

        sigma_layer = material_sigma(layer.material, sigma_overrides)
        Gprime += sigma_layer * shell_area

        details.append({
            "kind": "shell",
            "material": layer.material,
            "diameter_um": running_d_um,
            "shell_added_diameter_um": layer.added_diameter_um,
            "area_m2": shell_area,
            "sigma_s_per_m": sigma_layer,
            "sigmaA": sigma_layer * shell_area,
        })

        prev_area = new_area

    return Gprime, details


def solve_required_outer_added_diameter(
    target_Gprime: float,
    core_material: str,
    core_diameter_um: float,
    intermediate_layers: List[Layer],
    final_coating_material: str,
    sigma_overrides: dict[str, float],
) -> float:
    """
    Solve for the required TOTAL ADDED DIAMETER of the final coating material
    needed to achieve target_Gprime.

    Returns:
      added_diameter_um of the final coating
    """
    if target_Gprime <= 0:
        raise ValueError("Target conductance must be > 0")

    base_Gprime, base_details = layered_conductance_per_length(
        core_material=core_material,
        core_diameter_um=core_diameter_um,
        layers=intermediate_layers,
        sigma_overrides=sigma_overrides,
    )

    sigma_final = material_sigma(final_coating_material, sigma_overrides)

    if sigma_final <= 0:
        raise ValueError("Final coating conductivity must be > 0")

    # Current outer diameter after core + intermediate layers
    current_d_um = core_diameter_um + sum(layer.added_diameter_um for layer in intermediate_layers)
    current_area = circular_area_from_diameter_um(current_d_um)

    if base_Gprime >= target_Gprime:
        # No extra final coating needed to reach/exceed target
        return 0.0

    # Need additional shell area:
    # target_G = base_G + sigma_final * A_shell_needed
    A_shell_needed = (target_Gprime - base_Gprime) / sigma_final

    if A_shell_needed < 0:
        return 0.0

    required_total_area = current_area + A_shell_needed
    required_radius_m = math.sqrt(required_total_area / math.pi)
    required_total_d_um = 2.0 * required_radius_m * 1e6

    added_d_um = required_total_d_um - current_d_um
    if added_d_um < 0:
        return 0.0
    return added_d_um


def describe_layers(core_material: str, core_diameter_um: float, layers: List[Layer]) -> str:
    pieces = [f"{core_diameter_um:g} um {core_material} core"]
    for layer in layers:
        pieces.append(f"{layer.added_diameter_um:g} um total added {layer.material}")
    return " + ".join(pieces)


def main():
    parser = argparse.ArgumentParser(
        description="Solve required outer coating added diameter to match reference wire conductivity."
    )

    # Reference wire
    parser.add_argument(
        "--ref-core-material",
        default="tungsten",
        help="Reference core material (default: tungsten)"
    )
    parser.add_argument(
        "--ref-core-d-um",
        type=float,
        default=20.0,
        help="Reference core diameter in um (default: 20.0)"
    )
    parser.add_argument(
        "--ref-layer",
        action="append",
        default=[],
        help=(
            "Reference coating layer as material:added_diameter_um. "
            "Can be given multiple times. Default reference is 0.3 um total added gold diameter "
            "if no --ref-layer is provided."
        )
    )

    # Candidate wire
    parser.add_argument(
        "--core-material",
        required=True,
        help="Candidate core material, e.g. cf, tungsten, aluminum, stainless_steel"
    )
    parser.add_argument(
        "--core-d-um",
        type=float,
        required=True,
        help="Candidate core diameter in um"
    )
    parser.add_argument(
        "--intermediate-layer",
        action="append",
        default=[],
        help=(
            "Intermediate layer as material:added_diameter_um. "
            "Can be given multiple times, e.g. --intermediate-layer nickel:0.5"
        )
    )
    parser.add_argument(
        "--final-coating-material",
        required=True,
        help="Final outer coating material to solve for, e.g. gold, silver, nickel, copper"
    )

    # Optional conductivity overrides
    parser.add_argument(
        "--sigma-override",
        action="append",
        default=[],
        help=(
            "Override conductivity as material=value in S/m, "
            "e.g. --sigma-override cf=2.5e5"
        )
    )

    args = parser.parse_args()

    sigma_overrides = parse_sigma_override(args.sigma_override)

    # Default reference layer if not explicitly given
    if args.ref_layer:
        ref_layers = parse_layer_list(args.ref_layer)
    else:
        ref_layers = [Layer(material="gold", added_diameter_um=0.3)]

    candidate_intermediate_layers = parse_layer_list(args.intermediate_layer)

    # Compute target conductance
    target_Gprime, target_details = layered_conductance_per_length(
        core_material=args.ref_core_material.lower(),
        core_diameter_um=args.ref_core_d_um,
        layers=ref_layers,
        sigma_overrides=sigma_overrides,
    )

    # Solve required final coating
    needed_added_d_um = solve_required_outer_added_diameter(
        target_Gprime=target_Gprime,
        core_material=args.core_material.lower(),
        core_diameter_um=args.core_d_um,
        intermediate_layers=candidate_intermediate_layers,
        final_coating_material=args.final_coating_material.lower(),
        sigma_overrides=sigma_overrides,
    )

    # Compute matched candidate details
    full_candidate_layers = list(candidate_intermediate_layers) + [
        Layer(material=args.final_coating_material.lower(), added_diameter_um=needed_added_d_um)
    ]
    candidate_Gprime, candidate_details = layered_conductance_per_length(
        core_material=args.core_material.lower(),
        core_diameter_um=args.core_d_um,
        layers=full_candidate_layers,
        sigma_overrides=sigma_overrides,
    )

    candidate_total_d_um = args.core_d_um + sum(layer.added_diameter_um for layer in full_candidate_layers)

    print("=== Reference wire ===")
    print(describe_layers(args.ref_core_material.lower(), args.ref_core_d_um, ref_layers))
    print(f"Target axial conductance per unit length G' = {target_Gprime:.12g} S·m")
    print(f"Reference resistance per unit length R' = {1.0/target_Gprime:.12g} ohm/m")
    print()

    print("=== Candidate matched wire ===")
    print(f"Core: {args.core_d_um:g} um {args.core_material.lower()}")
    if candidate_intermediate_layers:
        print("Intermediate layers:")
        for layer in candidate_intermediate_layers:
            print(f"  - {layer.material}: {layer.added_diameter_um:g} um total added diameter")
    else:
        print("Intermediate layers: none")

    print(f"Required final coating material: {args.final_coating_material.lower()}")
    print(f"Required final coating added diameter = {needed_added_d_um:.12g} um")
    print(f"Equivalent final coating radial thickness = {0.5 * needed_added_d_um:.12g} um")
    print(f"Final total wire diameter = {candidate_total_d_um:.12g} um")
    print()

    print(f"Matched axial conductance per unit length G' = {candidate_Gprime:.12g} S·m")
    print(f"Matched resistance per unit length R' = {1.0/candidate_Gprime:.12g} ohm/m")
    print(f"Relative conductance mismatch = {(candidate_Gprime/target_Gprime - 1.0):.6e}")
    print()

    print("=== Conductivity values used ===")
    used_materials = {args.ref_core_material.lower(), args.core_material.lower(), args.final_coating_material.lower()}
    used_materials.update(layer.material for layer in ref_layers)
    used_materials.update(layer.material for layer in candidate_intermediate_layers)

    for mat in sorted(used_materials):
        sigma = material_sigma(mat, sigma_overrides)
        source = "override" if mat in sigma_overrides else "built-in"
        print(f"  {mat:16s}  sigma = {sigma:.12g} S/m  ({source})")


if __name__ == "__main__":
    main()