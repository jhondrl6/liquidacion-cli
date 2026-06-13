#!/usr/bin/env python3
"""
Script for generating test data for the settlement system.
Generates random cases and edge cases for comprehensive testing.

Author: Development Team
Date: 2025-11-04
Version: 1.0.0
"""

import argparse
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

import faker
from liquidator.utils.date_utils import get_current_year

# Configure Faker for Colombia
fake = faker.Faker('es_CO')


def generate_random_worker_profile(is_rural: bool = False) -> Dict[str, Any]:
    """Generates a random worker profile."""
    base_salary = random.choice([
        1423500,  # SMMLV
        2000000,
        2500000,
        3000000,
        4000000,
        5000000,
        1423500 * 2,  # Transportation allowance limit
        1423500 * 10  # High salary
    ])
    
    if random.random() < 0.3:  # 30% chance of variable salary
        base_salary = random.randint(1423500, 10000000)
    
    profile = {
        "name": fake.name(),
        "document": fake.random_number(digits=10),
        "contract_type": random.choice(["indefinido", "termino_fijo", "obra_o_labor"]),
        "start_date": generate_random_date(years_back=5),
        "lives_at_workplace": is_rural,
        "monthly_salary": base_salary
    }
    
    # Add variable components with certain probability
    if random.random() < 0.7:  # 70% have commissions
        profile["avg_monthly_commissions"] = random.uniform(0.1, 0.5) * base_salary
    
    if random.random() < 0.6:  # 60% have overtime
        profile["avg_monthly_overtime"] = random.uniform(0.05, 0.3) * base_salary
    
    if random.random() < 0.4:  # 40% have bonuses
        profile["avg_monthly_bonus"] = random.uniform(0.05, 0.2) * base_salary
    
    # Transportation allowance (only if not living at workplace)
    if not is_rural and base_salary <= (1423500 * 2) and random.random() < 0.8:
        profile["transportation_allowance"] = 200000
    
    # Connectivity allowance (with certain probability)
    if random.random() < 0.3:
        profile["connectivity_allowance"] = random.choice([50000, 70000, 100000, 150000])
    
    return profile


def generate_random_date(years_back: int = 0, years_forward: int = 0) -> str:
    """Generates a random date within a range of years."""
    current_year = get_current_year()
    start_date = datetime(current_year - years_back, 1, 1)
    end_date = datetime(current_year + years_forward, 12, 31)
    
    # Calculate difference in days
    delta_days = (end_date - start_date).days
    random_days = random.randint(0, delta_days)
    
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")


def generate_edge_case_date_scenarios() -> List[Dict[str, Any]]:
    """Generates edge cases for date scenarios."""
    current_year = get_current_year()
    cases = []
    
    # Case 1: First day of the year
    cases.append({
        "description": "Start employment first day of year",
        "start_date": f"{current_year}-01-01",
        "end_date": f"{current_year}-12-31"
    })
    
    # Case 2: Last day of the year
    cases.append({
        "description": "Start employment last day of year",
        "start_date": f"{current_year}-12-31",
        "end_date": f"{current_year}-12-31"
    })
    
    # Case 3: Leap year
    cases.append({
        "description": "Period including leap year",
        "start_date": f"{current_year-1}-01-01",
        "end_date": f"{current_year}-02-29" if current_year % 4 == 0 else f"{current_year}-02-28"
    })
    
    # Case 4: Day before and after semester change
    cases.append({
        "description": "End of semester (June 30)",
        "start_date": f"{current_year}-01-01",
        "end_date": f"{current_year}-06-30"
    })
    
    cases.append({
        "description": "Start second semester (July 1)",
        "start_date": f"{current_year}-01-01",
        "end_date": f"{current_year}-07-01"
    })
    
    # Case 5: Period crossing Sunday surcharge date (2025-07-01)
    cases.append({
        "description": "Period crossing Sunday surcharge date (2025-07-01)",
        "start_date": "2025-06-15",
        "end_date": "2025-07-15"
    })
    
    return cases


def generate_edge_case_salary_scenarios() -> List[Dict[str, Any]]:
    """Generates edge cases for salary scenarios."""
    smmlv = 1423500
    cases = []
    
    # Case 1: Exactly minimum wage
    cases.append({
        "description": "Current legal monthly minimum wage",
        "monthly_salary": smmlv,
        "transportation_allowance": 200000
    })
    
    # Case 2: Exactly 2 SMMLV (transportation allowance limit)
    cases.append({
        "description": "Salary exactly 2 SMMLV (transportation allowance limit)",
        "monthly_salary": smmlv * 2,
        "transportation_allowance": 200000
    })
    
    # Case 3: One peso above transportation allowance limit
    cases.append({
        "description": "Salary one peso above transportation allowance limit",
        "monthly_salary": smmlv * 2 + 1,
        "transportation_allowance": 0
    })
    
    # Case 4: High salary with indemnification cap
    cases.append({
        "description": "High salary (subject to indemnification cap of 20 SMMLV)",
        "monthly_salary": smmlv * 50,
        "note": "This case will test the max indemnification cap of 20 SMMLV"
    })
    
    # Case 5: Rural farm worker (no transportation allowance)
    cases.append({
        "description": "Rural farm worker (lives at workplace)",
        "monthly_salary": smmlv * 1.5,
        "lives_at_workplace": True,
        "note": "This case should exclude transportation allowance"
    })
    
    # Case 6: Variable salary (12-month average)
    salaries = []
    for i in range(12):
        month = f"{get_current_year()}-{str(i+1).zfill(2)}"
        base = smmlv * 1.5
        # Random variation between -30% and +50%
        variation = random.uniform(-0.3, 0.5)
        salary = base * (1 + variation)
        salaries.append({
            "period": month,
            "total": round(salary, 0)
        })
    
    cases.append({
        "description": "Variable salary (12 months with variation)",
        "historical_salaries": salaries,
        "note": "This case will test average calculations for variable salaries"
    })
    
    return cases


def generate_compliance_edge_cases() -> List[Dict[str, Any]]:
    """Generates specific edge cases for compliance tests."""
    cases = []
    
    # Case 1: Service provision contract (should fail)
    cases.append({
        "description": "Service provision contract (should fail compliance)",
        "contract_type": "prestacion_servicios",
        "monthly_salary": 3000000,
        "start_date": generate_random_date(),
        "end_date": generate_random_date(years_forward=1),
        "expected_compliance": "FAIL",
        "expected_rule": "V002"
    })
    
    # Case 2: Transportation allowance incorrectly applied in rural farm
    cases.append({
        "description": "Transportation allowance applied to rural farm worker (should fail)",
        "contract_type": "indefinido",
        "monthly_salary": 2000000,
        "lives_at_workplace": True,
        "transportation_allowance": 200000,
        "start_date": generate_random_date(),
        "end_date": generate_random_date(years_forward=1),
        "expected_compliance": "FAIL",
        "expected_rule": "V003"
    })
    
    # Case 3: Vacations included in periodic settlement
    cases.append({
        "description": "Vacations included in PERIODIC mode (should fail)",
        "mode": "PERIODIC",
        "pending_vacation_days": 15,
        "monthly_salary": 2500000,
        "start_date": generate_random_date(),
        "end_date": generate_random_date(years_forward=1),
        "expected_compliance": "FAIL",
        "expected_rule": "V007"
    })
    
    return cases


def generate_random_test_case(is_rural: bool = False, mode: str = "PERIODIC") -> Dict[str, Any]:
    """Generates a complete random test case."""
    worker = generate_random_worker_profile(is_rural)
    
    # Determine cutoff date
    if mode == "PERIODIC":
        # For periodic settlement, use end of year
        current_year = get_current_year()
        end_date = f"{current_year}-12-31"
    else:
        # For final settlement, use random date after start
        start_date = datetime.strptime(worker["start_date"], "%Y-%m-%d")
        max_days = (datetime(get_current_year() + 1, 12, 31) - start_date).days
        random_days = random.randint(1, min(max_days, 365 * 3))  # Maximum 3 years
        end_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    test_case = {
        "mode": mode,
        "start_date": worker["start_date"],
        "end_date": end_date,
        "monthly_salary": worker["monthly_salary"],
        "contract_type": worker["contract_type"]
    }
    
    # Copy salary components if they exist
    salary_components = [
        "avg_monthly_commissions",
        "avg_monthly_overtime",
        "avg_monthly_bonus",
        "transportation_allowance",
        "connectivity_allowance"
    ]
    
    for component in salary_components:
        if component in worker:
            test_case[component] = worker[component]
    
    # Add specific fields for final settlement
    if mode == "FINIQUITO":
        test_case["pending_vacation_days"] = random.randint(0, 15)
        test_case["termination_reason"] = random.choice([
            "sin_justa_causa", 
            "con_justa_causa", 
            "renuncia", 
            "mutuo_acuerdo"
        ])
    
    # Add residence field if applicable
    if "lives_at_workplace" in worker:
        test_case["lives_at_workplace"] = worker["lives_at_workplace"]
    
    return test_case


def generate_test_suite(num_random: int = 20, include_edge_cases: bool = True) -> Dict[str, Any]:
    """Generates a complete test suite."""
    test_suite = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "description": "Automatically generated test suite for the settlement system"
        },
        "test_cases": []
    }
    
    # Generate random cases
    for i in range(num_random):
        is_rural = random.random() < 0.2  # 20% chance of being rural farm
        mode = "PERIODIC" if random.random() < 0.7 else "FINIQUITO"  # 70% periodic, 30% final settlement
        
        test_case = generate_random_test_case(is_rural, mode)
        test_case["case_id"] = f"random_{i+1}"
        test_case["category"] = "random"
        test_case["expected_behavior"] = "standard"
        
        test_suite["test_cases"].append(test_case)
    
    # Add edge cases if requested
    if include_edge_cases:
        # Date edge cases
        date_cases = generate_edge_case_date_scenarios()
        for i, case in enumerate(date_cases):
            test_case = {
                "case_id": f"edge_date_{i+1}",
                "category": "edge_case",
                "subcategory": "date",
                "mode": "PERIODIC",
                "start_date": case["start_date"],
                "end_date": case["end_date"],
                "monthly_salary": 2000000,
                "contract_type": "indefinido",
                "description": case["description"]
            }
            test_suite["test_cases"].append(test_case)
        
        # Salary edge cases
        salary_cases = generate_edge_case_salary_scenarios()
        for i, case in enumerate(salary_cases):
            test_case = {
                "case_id": f"edge_salary_{i+1}",
                "category": "edge_case",
                "subcategory": "salary",
                "mode": "PERIODIC",
                "start_date": generate_random_date(years_back=1),
                "end_date": f"{get_current_year()}-12-31",
                "monthly_salary": case["monthly_salary"],
                "contract_type": "indefinido",
                "description": case["description"]
            }
            
            # Copy other fields from the edge case
            for key, value in case.items():
                if key not in ["description", "monthly_salary"]:
                    test_case[key] = value
            
            test_suite["test_cases"].append(test_case)
        
        # Compliance edge cases
        compliance_cases = generate_compliance_edge_cases()
        for i, case in enumerate(compliance_cases):
            test_case = {
                "case_id": f"compliance_{i+1}",
                "category": "compliance_validation",
                "mode": case.get("mode", "PERIODIC"),
                "description": case["description"],
                "expected_compliance": case["expected_compliance"],
                "expected_rule": case["expected_rule"]
            }
            
            # Copy all fields from the case
            for key, value in case.items():
                if key not in ["description", "expected_compliance", "expected_rule"]:
                    test_case[key] = value
            
            test_suite["test_cases"].append(test_case)
    
    return test_suite


def save_test_suite(test_suite: Dict[str, Any], output_dir: str, filename: str):
    """Saves the test suite to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_suite, f, indent=2, ensure_ascii=False)
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Test data generator for settlement system')
    parser.add_argument('--num-random', type=int, default=20,
                        help='Number of random cases to generate (default: 20)')
    parser.add_argument('--no-edge-cases', action='store_false', dest='include_edge_cases',
                        help='Do not include edge cases in generation')
    parser.add_argument('--output-dir', default='liquidator/tests/fixtures/generated',
                        help='Output directory for generated files')
    parser.add_argument('--filename', default=f'test_cases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                        help='Output filename')
    parser.add_argument('--seed', type=int,
                        help='Seed for reproducible random generation')
    
    args = parser.parse_args()
    
    # Configure paths
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Set seed if provided
    if args.seed:
        random.seed(args.seed)
        fake.seed_instance(args.seed)
        print(f"[INFO] Seed set for reproducible generation: {args.seed}")
    
    print(f"[INFO] Generating test suite with {args.num_random} random cases...")
    if args.include_edge_cases:
        print("[INFO] Including edge cases for dates, salaries and compliance...")
    
    # Generate test suite
    test_suite = generate_test_suite(
        num_random=args.num_random,
        include_edge_cases=args.include_edge_cases
    )
    
    # Save suite
    output_path = save_test_suite(test_suite, args.output_dir, args.filename)
    
    print(f"\n[SUCCESS] Test suite generated successfully")
    print(f"[INFO] Total cases generated: {len(test_suite['test_cases'])}")
    print(f"[INFO] - Random cases: {args.num_random}")
    print(f"[INFO] - Edge cases: {len(test_suite['test_cases']) - args.num_random}")
    print(f"[INFO] File saved to: {output_path}")
    
    # Show category summary
    categories = {}
    for test_case in test_suite["test_cases"]:
        category = test_case["category"]
        categories[category] = categories.get(category, 0) + 1
    
    print("\n[INFO] Category summary:")
    for category, count in categories.items():
        print(f"   - {category}: {count} cases")
    
    return 0


if __name__ == "__main__":
    exit(main())