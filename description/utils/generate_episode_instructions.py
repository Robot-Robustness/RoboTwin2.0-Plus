import json
import re
from typing import List, Dict, Any
import os
import argparse
import random
import yaml

current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path)


def extract_placeholders(instruction: str) -> List[str]:
    """Extract all placeholders of the form {X} from an instruction."""
    placeholders = re.findall(r"{([^}]+)}", instruction)
    return placeholders

def filter_instructions(instructions: List[str], episode_params: Dict[str, str]) -> List[str]:
    """
    Filter instructions to only include those that have all placeholders
    matching the available episode parameters. No more, no less.
    Also accept instructions that don't contain arm placeholder {[a-z]}.
    """
    filtered_instructions = []
    random.shuffle(instructions)

    for instruction in instructions:
        placeholders = extract_placeholders(instruction)
        # Remove {} from episode_params keys for comparison
        stripped_episode_params = {key.strip("{}"): value for key, value in episode_params.items()}

        # Get all arm-related parameters (single lowercase letters)
        arm_params = {key for key in stripped_episode_params.keys() if len(key) == 1 and "a" <= key <= "z"}
        non_arm_params = set(stripped_episode_params.keys()) - arm_params

        # Accept if we have exact match OR if the only missing parameters are arm parameters
        if set(placeholders) == set(stripped_episode_params.keys()) or (
                # Special case: accept if the only difference is missing arm parameters
                arm_params and set(placeholders).union(arm_params) == set(stripped_episode_params.keys()) and
                not arm_params.intersection(set(placeholders))):
            filtered_instructions.append(instruction)

    return filtered_instructions


def replace_placeholders(instruction: str, episode_params: Dict[str, str]) -> str:
    """Replace all {X} placeholders in the instruction with corresponding values from episode_params.
    For arm placeholders {[a-z]}, add 'the ' in front and ' arm' after the value.
    If the value is a path to an existing JSON file, randomly choose one 'description' item and prepend 'the'.
    If the value contains '\' or '/' but the file does not exist, print a bold warning.
    """
    # Remove {} from episode_params keys for replacement
    stripped_episode_params = {key.strip("{}"): value for key, value in episode_params.items()}

    for key, value in stripped_episode_params.items():
        placeholder = "{" + key + "}"
        # Check if the value contains '\' or '/'
        if "\\" in value or "/" in value:
            json_path = os.path.join(
                os.path.join(parent_directory, "../objects_description"),
                value + ".json",
            )
            if not os.path.exists(json_path):
                print(f"\033[1mERROR: '{json_path}' looks like a description file, but does not exist.\033[0m")
                exit()

        # Check if the value is a path to an existing JSON file
        json_path = os.path.join(os.path.join(parent_directory, "../objects_description"), value + ".json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                json_data = json.load(f)
            # Randomly choose one description and prepend 'the'
            description = random.choice(json_data.get("seen", []))
            value = f"the {description}"
        # Check if the key is a single lowercase letter (arm placeholder)
        elif len(key) == 1 and "a" <= key <= "z":
            value = f"the {value} arm"
        else:
            value = f"{value}"

        instruction = instruction.replace(placeholder, value)

    return instruction


def replace_placeholders_unseen(instruction: str, episode_params: Dict[str, str]) -> str:
    """Similar to replace_placeholders but uses 'unseen' descriptions from JSON files.
    For arm placeholders {[a-z]}, add 'the ' in front and ' arm' after the value.
    If the value is a path to an existing JSON file, randomly choose one 'unseen' description and prepend 'the'.
    If the value contains '\' or '/' but the file does not exist, print a bold warning.
    """
    # Remove {} from episode_params keys for replacement
    stripped_episode_params = {key.strip("{}"): value for key, value in episode_params.items()}

    for key, value in stripped_episode_params.items():
        placeholder = "{" + key + "}"
        # Check if the value contains '\' or '/'
        if "\\" in value or "/" in value:
            json_path = os.path.join(
                os.path.join(parent_directory, "../objects_description"),
                value + ".json",
            )
            if not os.path.exists(json_path):
                print(f"\033[1mERROR: '{json_path}' looks like a description file, but does not exist.\033[0m")
                exit()

        # Check if the value is a path to an existing JSON file
        json_path = os.path.join(os.path.join(parent_directory, "../objects_description"), value + ".json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                json_data = json.load(f)
            # Randomly choose one unseen description and prepend 'the'
            if "unseen" in json_data and json_data["unseen"]:
                description = random.choice(json_data.get("unseen", []))
                value = f"the {description}"
            else:
                # Fall back to seen descriptions if unseen is empty
                description = random.choice(json_data.get("seen", []))
                value = f"the {description}"
        # Check if the key is a single lowercase letter (arm placeholder)
        elif len(key) == 1 and "a" <= key <= "z":
            value = f"the {value} arm"
        else:
            value = f"{value}"

        instruction = instruction.replace(placeholder, value)

    return instruction




    
def load_task_instructions(task_name: str) -> Dict[str, Any]:
    """Load the task instructions from the JSON file."""
    file_path = os.path.join(parent_directory, f"../task_instruction/{task_name}.json")
    with open(file_path, "r") as f:
        task_data = json.load(f)
    return task_data


# ────────────────────────────────────────────────
# RoboTwin-Plus: Load pre-generated R2/R3 instruction variants
# ────────────────────────────────────────────────
def load_plus_instructions(task_name: str) -> Dict[str, Any]:
    """Load pre-generated R1/R2/R3 instruction variants from task_instruction_plus/."""
    # Look relative to this file's parent (description/utils/) -> description/task_instruction_plus/
    # Also check the robotwin_plus directory structure
    candidates = [
        os.path.join(parent_directory, f"../task_instruction_plus/{task_name}.json"),
        os.path.join(parent_directory, f"../../task_instruction_plus/{task_name}.json"),
    ]
    for file_path in candidates:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    print(f"[Language Plus] WARNING: No plus instructions found for '{task_name}'")
    return {}


def load_scene_info(task_name: str, setting: str, scene_info_path: str) -> Dict[str, Dict]:
    """Load the scene info from the JSON file in the data directory."""
    file_path = os.path.join(parent_directory, f"../../{scene_info_path}/{task_name}/{setting}/scene_info.json")
    try:
        with open(file_path, "r") as f:
            scene_data = json.load(f)
        return scene_data
    except FileNotFoundError:
        print(f"\033[1mERROR: Scene info file '{file_path}' not found.\033[0m")
        exit(1)
    except json.JSONDecodeError:
        print(f"\033[1mERROR: Scene info file '{file_path}' contains invalid JSON.\033[0m")
        exit(1)


def extract_episodes_from_scene_info(scene_info: Dict) -> List[Dict[str, str]]:
    """Extract episode parameters from scene_info."""
    episodes = []
    for episode_key, episode_data in scene_info.items():
        if "info" in episode_data:
            episodes.append(episode_data["info"])
        else:
            episodes.append(dict())
    return episodes


def save_episode_descriptions(task_name: str, setting: str, generated_descriptions: List[Dict]):
    """Save generated descriptions to output files."""
    output_dir = os.path.join(parent_directory, f"../../data/{task_name}/{setting}/instructions")
    os.makedirs(output_dir, exist_ok=True)

    for episode_desc in generated_descriptions:
        episode_index = episode_desc["episode_index"]
        output_file = os.path.join(output_dir, f"episode{episode_index}.json")


        # Save only what was generated
        save_dict = {}
        for key in ["seen", "unseen", "r1_distraction", "r2_commonsense", "r3_reasoning"]:
            if key in episode_desc:
                save_dict[key] = episode_desc[key]

        with open(output_file, "w") as f:
            json.dump(save_dict, f, indent=2)


# def generate_episode_descriptions(task_name: str, episodes: List[Dict[str, str]], max_descriptions: int = 1000000):
def generate_episode_descriptions(task_name: str, episodes: List[Dict[str, str]], max_descriptions: int = 1000000, perturb: str = "seen"):   # ← ADD THIS
    """
    Generate descriptions for episodes by replacing placeholders in instructions with parameter values.
    For each episode, filter instructions that have matching placeholders and generate up to
    max_descriptions by replacing placeholders with parameter values.
    Now also generates unseen descriptions.
    """
    # Load task instructions
    task_data = load_task_instructions(task_name)
    seen_instructions = task_data.get("seen", [])
    unseen_instructions = task_data.get("unseen", [])

    # Store generated descriptions for each episode
    all_generated_descriptions = []




    # ────────────────────────────────────────────────
    # NEW: R1 Distraction post-processing (LIBERO-Plus style)
    # ────────────────────────────────────────────────
    def make_r1_distraction(base: str) -> str:
        if not base.strip():
            return base
        prefixes = [
            "Hey, before we do anything else, could you please ",
            "Just so everything is ready, make sure to ",
            "Quick reminder — while you're here, ",
            "Alright, let's handle this first: ",
            "If it's not too much trouble, would you mind to ",
            "Before we move on or touch other things, ",
            "So first things first, go ahead and ",
            "To keep things organized and safe, ",
            "Hey robot, could you please ",
            "Quick thing — make sure to ",
            "Hi there, go ahead and ",
            "Before we start, please ",
            "Hey, just do this first: ",
            "Alright, let's handle ",
            "Quick reminder — ",
            "Hey robot, would you mind ",
            "Hi, make sure to ",
            "Before anything else, ",
            "Hey there, please ",
            "Let's take care of this: ",
            "Quick note — go ahead and ",
            "Hello, could you ",
            "Hey robot, first off ",
            "Hi there, just make sure ",
            "Before we move on, ",
            "Alright, please do ",
            "Hey, one small step — ",
            "Quick check — ",
            "Hi robot, go for it: ",
            "Hey there, would you please ",
            "Hello, make sure to ",
            "Before we continue, ",
            "Hey robot, how are you doing? Could you ",
            "Quick hello — please ",
            "Hi, let's do this: ",
            "Hey, before we get going, ",
            "Alright, first thing — ",
            "Hello there, go ahead and ",
            "Hey robot, everything good? Then please ",
            "Quick reminder, make sure to ",
            "Hi there, could you please ",
            "Before the next step, ",
            "Hey, just this one thing: ",
            "Hello, would you mind to ",
            "Quick note — ",
            "Hey robot, hope you're running smoothly — go ahead and ",
            "Hi, please make sure ",
            "Alright, let's start with ",
            "Hey there, before we do more, ",
            "Hello, quick task — ",
            "Hey robot, all set? Then ",
            "Quick check-in — please ",
            "Hi there, make sure to ",
            "Before anything else happens, ",
            "Hey, one moment — could you ",
            "Hello robot, feeling ready? If so, ",
            "Quick thing before we continue — ",
            "Hey robot, good to see you — please "

        ]
        p = random.choice(prefixes)
        instr_lower = base[0].lower() + base[1:] 
        return p + instr_lower
    # ────────────────────────────────────────────────



    # Process each episode
    for i, episode in enumerate(episodes):
        # Filter instructions that have all placeholders matching episode parameters
        filtered_seen_instructions = filter_instructions(seen_instructions, episode)
        filtered_unseen_instructions = filter_instructions(unseen_instructions, episode)

        if filtered_seen_instructions == [] and filtered_unseen_instructions == []:
            print(f"Episode {i}: No valid instructions found")
            continue

        # Generate seen descriptions by replacing placeholders
        seen_episode_descriptions = []
        flag_seen = True
        while (len(seen_episode_descriptions) < max_descriptions and flag_seen and filtered_seen_instructions):
            
            for instruction in filtered_seen_instructions:
                if len(seen_episode_descriptions) >= max_descriptions:
                    flag_seen = False
                    break
                description = replace_placeholders(instruction, episode)
                seen_episode_descriptions.append(description)

        # Generate unseen descriptions by replacing placeholders
        unseen_episode_descriptions = []
        flag_unseen = True
        while (len(unseen_episode_descriptions) < max_descriptions and flag_unseen and filtered_unseen_instructions):
            for instruction in filtered_unseen_instructions:
                if len(unseen_episode_descriptions) >= max_descriptions:
                    flag_unseen = False
                    break
                description = replace_placeholders_unseen(instruction, episode)
                unseen_episode_descriptions.append(description)

        # all_generated_descriptions.append({
        #     "episode_index": i,
        #     "seen": seen_episode_descriptions,
        #     "unseen": unseen_episode_descriptions,
        # })

        episode_dict = {
            "episode_index": i,
            "seen": seen_episode_descriptions,
            "unseen": unseen_episode_descriptions,
        }




        # ────────────────────────────────────────────────
        # NEW: if perturb == "r1", add distraction versions
        # ────────────────────────────────────────────────
        if perturb == "r1":
            r1_list = []
            base_pool = unseen_episode_descriptions if unseen_episode_descriptions else seen_episode_descriptions
            random.shuffle(base_pool)
            for base in base_pool:
                if len(r1_list) >= max_descriptions:
                    break
                r1_list.append(make_r1_distraction(base))
            episode_dict["r1_distraction"] = r1_list
        # ────────────────────────────────────────────────

        # ────────────────────────────────────────────────
        # RoboTwin-Plus: R2 (common sense) and R3 (reasoning chain)
        # Uses pre-generated instruction variants from task_instruction_plus/
        # ────────────────────────────────────────────────
        if perturb in ("r2", "r3", "r1r2r3", "language_plus"):
            plus_data = load_plus_instructions(task_name)
            if plus_data:
                # R1 distraction: use pre-generated variants, instantiate placeholders
                if perturb in ("r1", "r1r2r3", "language_plus"):
                    r1_templates = plus_data.get("r1_distraction", [])
                    if r1_templates:
                        r1_filtered = filter_instructions(r1_templates, episode)
                        r1_descs = []
                        for tmpl in r1_filtered:
                            if len(r1_descs) >= max_descriptions:
                                break
                            r1_descs.append(replace_placeholders_unseen(tmpl, episode))
                        if not r1_descs:
                            # Fallback: use runtime R1 generation
                            base_pool = unseen_episode_descriptions if unseen_episode_descriptions else seen_episode_descriptions
                            for base in base_pool[:max_descriptions]:
                                r1_descs.append(make_r1_distraction(base))
                        episode_dict["r1_distraction"] = r1_descs

                # R2 commonsense: use pre-generated variants, instantiate placeholders
                if perturb in ("r2", "r1r2r3", "language_plus"):
                    r2_templates = plus_data.get("r2_commonsense", [])
                    if r2_templates:
                        r2_filtered = filter_instructions(r2_templates, episode)
                        r2_descs = []
                        for tmpl in r2_filtered:
                            if len(r2_descs) >= max_descriptions:
                                break
                            r2_descs.append(replace_placeholders_unseen(tmpl, episode))
                        episode_dict["r2_commonsense"] = r2_descs
                        if r2_descs:
                            print(f"  [R2] Episode {i}: {len(r2_descs)} commonsense variants")

                # R3 reasoning: use pre-generated variants, instantiate placeholders
                if perturb in ("r3", "r1r2r3", "language_plus"):
                    r3_templates = plus_data.get("r3_reasoning", [])
                    if r3_templates:
                        r3_filtered = filter_instructions(r3_templates, episode)
                        r3_descs = []
                        for tmpl in r3_filtered:
                            if len(r3_descs) >= max_descriptions:
                                break
                            r3_descs.append(replace_placeholders_unseen(tmpl, episode))
                        episode_dict["r3_reasoning"] = r3_descs
                        if r3_descs:
                            print(f"  [R3] Episode {i}: {len(r3_descs)} reasoning variants")
        # ────────────────────────────────────────────────

        all_generated_descriptions.append(episode_dict)



    return all_generated_descriptions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate episode descriptions by replacing placeholders")
    parser.add_argument(
        "task_name",
        type=str,
        help="Name of the task (JSON file name without extension)",
    )
    parser.add_argument(
        "setting",
        type=str,
        help="Setting name used to construct the data directory path",
    )
    parser.add_argument(
        "max_num",
        type=int,
        default=100,
        help="Maximum number of descriptions per episode",
    )

    args = parser.parse_args()
    setting_file = os.path.join(
        parent_directory, f"../../task_config/{args.setting}.yml"
    )
    with open(setting_file, "r", encoding="utf-8") as f:
        args_dict = yaml.load(f.read(), Loader=yaml.FullLoader)

    # Load scene info and extract episode parameters
    scene_info = load_scene_info(args.task_name, args.setting, args_dict['save_path'])
    episodes = extract_episodes_from_scene_info(scene_info)

    # RoboTwin-Plus: read language mode from YAML config
    language_config = args_dict.get("language", {})
    perturb_mode = language_config.get("mode", "seen") if isinstance(language_config, dict) else "seen"

    # Generate descriptions
    results = generate_episode_descriptions(args.task_name, episodes, args.max_num, perturb=perturb_mode)

    # Save results to output files
    save_episode_descriptions(args.task_name, args.setting, results)
    print("Successfully Saved Instructions")