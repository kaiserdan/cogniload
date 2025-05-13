import random
import json
import os
import sys
import argparse
from pathlib import Path

class CogniLoad:
    COLORS = ["blue", "red", "yellow", "green", "purple", "pink", "orange", "black", "white", "gray"]
    PEOPLE = [
        "Peter", "Paul", "Mary", "John", "Mark", "Jeff", "Craig", "Daniel", "Anna", "Arnoldo", "Ali", "Benjamin",
        "Joe", "Donald", "Mitch", "Chuck", "Jack", "Lucas", "Jeniffer", "Adam", "Greg", "Allan", "David", "Ellen",
        "Fred", "Hank", "Hubert", "Ian", "Ingrid", "Rebecca", "Ken", "Lewis", "Michael", "Nathaniel", "Oliver",
        "Russ", "Steve", "Sandy", "Ted", "Tanya", "Veronica", "Vincent", "Wesley", "Brad", "Sam", "Igor", "Sue",
        "Jan", "Jeffrey", "Jacques", "Debby", "Olivia", "Benedict", "Chris", "Charles", "Harry", "Eli", "Mahmoud",
        "Chen", "William", "Linda", "Elizabeth", "Robert", "Jennifer", "Emily", "Joseph", "Thomas", "Patricia",
        "Anthony", "Jessica", "Brian", "Lisa", "Kevin", "Karen", "Laura", "Eric", "Stephanie", "Michelle", "George",
        "Andrew", "Joshua", "Amber", "Timothy", "Victoria", "Richard", "Cynthia", "Brandon", "Megan", "Matthew",
        "Nancy", "Jacqueline", "Gary", "Dorothy", "Edward", "Kimberly", "Scott", "Sara", "Justin", "Brittany",
        "Ronald", "Deborah", "Janet", "Christopher", "Alexander", "Samantha", "Oscar", "Cindy", "Frank", "Carl",
        "Paula", "Irene", "Theresa", "Dennis", "Ralph", "Gerald", "Martin", "Terry", "Bryan", "Lance", "Corey",
        "Casey", "Brent", "Derek", "Travis", "Austin", "Victor", "Jesse", "Zachary", "Kyle", "Aaron", "Betty",
        "Connie", "Holly", "Donna", "Gloria", "Carla", "Isabel", "Sylvia", "Evelyn", "Doris", "Arthur", "Raymond",
        "Harold", "Lawrence", "Neil", "Brenda", "Tracy", "Simon", "Wendy", "Zoe", "Ethan", "Calvin", "Sean", "Ruth",
        "Sheila", "Miriam", "Lorraine", "Fay", "Sophie"
    ]

    CATEGORIES_DATA = {
        "location": [
            "bathroom", "livingroom", "kitchen", "basement", "toilet", "balcony", "garden", "pool", "bedroom",
            "store", "university", "farm", "office", "bank", "tree", "museum", "school", "airport", "zoo",
            "train", "bus", "park", "butcher", "library", "restaurant", "mall", "mountain", "tunnel", "church",
            "river", "pond", "harbor", "taxi", "gallery", "bar", "pizzeria", "beach", "gym", "elevator",
            "insurance", "embassy", "police", "hospital", "festival", "monument", "laboratory", "observatory",
            "valley", "motorway", "viewpoint", "synagogue", "factory", "castle", "cave", "stadium", "arena",
            "cabin", "plaza", "amphitheater", "bridge", "pier", "vineyard", "forest", "cliff", "desert",
            "creek", "bay", "lighthouse", "orchard", "resort", "camp", "inn", "motel", "aquarium", "bazaar",
            "chapel", "monastery", "lookout", "campground", "retreat", "dock", "depot", "consulate", "manor",
            "theatre", "cathedral", "casino", "lodge", "mill", "bakery", "spa", "station", "diner", "gazebo",
            "terrace", "arcade", "boardwalk", "winery", "hill", "plateau", "ridge", "port", "oasis", "market",
            "fairground", "quarry", "mine", "grove", "auditorium", "cemetery", "dunes", "courthouse", "prison",
            "fort", "granary", "ranch", "promenade", "coliseum", "field", "tower", "pavilion", "silo", "bistro",
            "labyrinth", "cafe", "saloon", "brewery", "carnival", "marina", "estate", "safari", "cottage",
            "courtyard", "waterpark", "island", "greenhouse", "meadow", "lagoon", "ford", "hacienda", "village",
            "marketplace", "grotto", "maze", "golfcourse", "atrium", "academy", "waterfront", "peninsula",
            "cove", "summit", "plains"
        ],
        "clothes_shirt": COLORS,
        "clothes_pant": COLORS,
        "clothes_hat": COLORS,
        "clothes_socks": COLORS,
        "clothes_gloves": COLORS,
        "clothes_underwear": COLORS,
        "hair": COLORS,
        "recent_eat": ["pizza", "pasta", "burrito", "sushi", "taco", "burger", "toast", "egg", "banana", "potatoes"],
        "recent_watch": [
            "drama", "comedy", "thriller", "romance", "adventure", "horror", "sci-fi", "action", "western",
            "fantasy", "documentary", "mystery", "crime", "musical"
        ],
        "recent_listen": [
            "rock", "pop", "country", "electronic", "folk", "jazz", "blues", "classical", "funk", "ska", "rap",
            "synth", "disco", "reaggea"
        ],
        "recent_read": [
            "fiction", "mystery", "novel", "thriller", "biography", "sci-fi", "non-fiction", "essay",
            "encyclopedia", "dictionary"
        ],
    }
    CATEGORIES_LIST = list(CATEGORIES_DATA.keys())

    def __init__(self, original_seed, number_of_puzzles, num_grid, ratio_grid, difficulty_grid):
        self.original_seed = original_seed
        self.number_of_puzzles = number_of_puzzles
        self.num_grid = num_grid
        self.ratio_grid = ratio_grid
        self.difficulty_grid = difficulty_grid
        
    def _seed_rng(self, seed_val):
        random.seed(seed_val)

    def take_random(self, population, k):
        # returns all elements if N >= len(list)
        actual_k = min(k, len(population))
        return random.sample(population, actual_k)

    def rand_uniform_n(self, n):
        # Integer from 1 to N inclusive
        if n < 1: # Should not happen with difficulty >= 1
             return 1 
        return random.randint(1, n)

    def make_configs(self, num_statements_list, ratio_percent_list, difficulty_list):
        configs = []
        for n in num_statements_list:
            for ratio in ratio_percent_list:
                for diff in difficulty_list:
                    needles_float = n * ratio / 100
                    num_needles = int(round(needles_float))
                    num_needles = max(1, num_needles)
                    num_needles = min(num_needles, n)
                    configs.append({"num_statements": n, "needles": num_needles, "difficulty": diff})
        return configs

    def initialize_people(self, state):
        people = state['people']
        categories = state['categories']
        diff = state['difficulty']

        category_defaults = {}
        for category in categories:
            wanted = 3 if diff == 1 else diff + 1
            num_defaults = min(wanted, len(self.CATEGORIES_DATA[category]))
            category_defaults[category] = self.take_random(self.CATEGORIES_DATA[category], num_defaults)
        
        initial_history = {}
        for idx, person in enumerate(people):
            attrs = {}
            for category in categories:
                defaults = category_defaults[category]
                value = defaults[idx % len(defaults)]
                attrs[category] = value
            initial_history[person] = [attrs] # History is a list of states, newest first

        new_state = state.copy()
        new_state['history'] = initial_history
        new_state['poi_history'] = list(initial_history[state['poi']]) # Make a copy
        new_state['category_defaults'] = category_defaults
        new_state['operation_types'] = []
        new_state['statement_condition_length'] = []
        new_state['statement_update_length'] = []
        return new_state

    def pick_statement_type(self, state):
        needles = state['needles']
        hays = state['hays']
        
        rand_val = random.random() # [0.0, 1.0)
        total = needles + hays
        if total == 0: # Fallback to avoid division by zero, though problem constraints prevent this
            return 'needles' if needles > 0 else 'hays' # Fallback, though hays or needles should be >0

        if rand_val > (needles / total):
            return 'hays'
        else:
            return 'needles'

    def next_operation(self, operation_type, state):
        if operation_type == 'needles':
            return self.generate_operation(state['poi'], state)
        elif operation_type == 'hays':
            person_for_hays = random.choice(state['non_poi_people'])
            return self.generate_operation(person_for_hays, state)
        return {"error": "unknown_operation_type"} # Should not happen

    def formulate_statement(self, conditions, updates):
        
        condition_keys = list(conditions.keys())
        random.shuffle(condition_keys)
        
        update_keys = list(updates.keys())
        random.shuffle(update_keys)

        condition_clauses = []
        for cond_key in condition_keys:
            value = conditions[cond_key]
            clause = ""
            if cond_key == "location": clause = f"located in the {value}"
            elif cond_key == "clothes_shirt": clause = f"wearing a {value} shirt"
            elif cond_key == "clothes_pant": clause = f"wearing a {value} pant"
            elif cond_key == "clothes_hat": clause = f"wearing a {value} hat"
            elif cond_key == "clothes_socks": clause = f"wearing {value} socks"
            elif cond_key == "clothes_gloves": clause = f"wearing {value} gloves"
            elif cond_key == "clothes_underwear": clause = f"wearing {value} underwear"
            elif cond_key == "hair": clause = f"having {value} hair"
            elif cond_key == "recent_eat": clause = f"which most recently ate {value}"
            elif cond_key == "recent_watch": clause = f"which most recently watched a {value} movie"
            elif cond_key == "recent_listen": clause = f"which most recently listened to {value} music"
            elif cond_key == "recent_read": clause = f"which most recently read a {value} book"
            condition_clauses.append(clause)
        
        condition_statement = "The people " + " and ".join(condition_clauses)

        update_clauses = []
        for upd_key in update_keys:
            value = updates[upd_key]
            clause = ""
            if upd_key == "location": clause = f"move to the {value}"
            elif upd_key == "clothes_shirt": clause = f"change into a {value} shirt"
            elif upd_key == "clothes_pant": clause = f"change into a {value} pant"
            elif upd_key == "clothes_hat": clause = f"change into a {value} hat"
            elif upd_key == "clothes_socks": clause = f"change into {value} socks"
            elif upd_key == "clothes_gloves": clause = f"put on {value} gloves"
            elif upd_key == "clothes_underwear": clause = f"put on {value} underwear"
            elif upd_key == "hair": clause = f"color their hair to {value}"
            elif upd_key == "recent_eat": clause = f"eat a {value}"
            elif upd_key == "recent_watch": clause = f"watch a {value} movie"
            elif upd_key == "recent_listen": clause = f"listen to {value} music"
            elif upd_key == "recent_read": clause = f"read a {value} book"
            update_clauses.append(clause)
            
        update_statement = " and ".join(update_clauses)
        
        return f"{condition_statement} {update_statement}"

    def update_history(self, conditions, updates, current_history):
        new_history = {}
        for person, person_hist_list in current_history.items():
            most_recent_person_state = person_hist_list[0]
            
            all_conditions_match = True
            if not conditions: # If conditions are empty, it matches by definition for an update
                pass
            else:
                for cond_key, cond_val in conditions.items():
                    if most_recent_person_state.get(cond_key) != cond_val:
                        all_conditions_match = False
                        break
            
            if all_conditions_match:
                # Apply updates
                updated_person_state = most_recent_person_state.copy()
                for prop_key, prop_val in updates.items():
                    updated_person_state[prop_key] = prop_val
                new_history[person] = [updated_person_state] + person_hist_list
            else:
                # No change
                new_history[person] = list(person_hist_list) # copy list
        return new_history

    def validate_conditions(self, conditions, updates, history, poi, last_poi_state):
        # Ensure it doesn't affect POI if conditions match POI's state
        poi_matches_conditions = True
        if not conditions: # Empty conditions means it applies to POI for update purposes
             pass
        else:
            for cond_key, cond_val in conditions.items():
                if last_poi_state.get(cond_key) != cond_val:
                    poi_matches_conditions = False
                    break
        
        if poi_matches_conditions:
            return {"status": "err", "type": "invalid_non_poi_update_effects_poi", "data": (updates, conditions)}

        # Ensure it affects at least one non-POI and check resulting states
        non_poi_people = [p for p in history if p != poi] # List of non-POI names
        
        non_pois_affected = [] # List of non-POI names that match the 'conditions'
        for person_name_iter in non_poi_people:
            non_poi_last_s = history[person_name_iter][0]
            matches = True
            if not conditions: # Empty conditions implies matches
                pass
            else:
                for cond_key, cond_val in conditions.items():
                    if non_poi_last_s.get(cond_key) != cond_val:
                        matches = False
                        break
            if matches:
                non_pois_affected.append(person_name_iter)

        if not non_pois_affected:
            return {"status": "err", "type": "non_poi_statement_affects_nobody", "data": (updates, conditions)}

        # Check 1: Would *every* affected non‑POI equal the POI afterwards?
        all_affected_non_pois_become_equal_to_poi = True
        if not non_pois_affected : # Should not happen due to check above, but for safety
            all_affected_non_pois_become_equal_to_poi = False 
        else:
            for person_name_iter in non_pois_affected:
                # Prospective state of this affected non-POI
                prospective_state = {**history[person_name_iter][0], **updates}
                if prospective_state != last_poi_state:
                    all_affected_non_pois_become_equal_to_poi = False
                    break
        
        if all_affected_non_pois_become_equal_to_poi:
            return {"status": "err", "type": "non_poi_update_makes_all_states_equal_poi", "data": (updates, conditions)}

        # Check 2: all_non_poi_identical
        map_step_result = []
        for p_name_hist, p_history_list in history.items(): # p_name_hist can be POI or non-POI
            p_last_s = p_history_list[0]
            # non_pois_affected is a list of non-POI names.
            if p_name_hist in non_pois_affected: # True if p_name_hist is a non-POI and is affected
                map_step_result.append({**p_last_s, **updates})
            else: # This covers the POI, and non-POIs not in non_pois_affected
                map_step_result.append(p_last_s.copy()) 

        # This rejects plain maps (all our states) and keeps structs.
        reject_step_result = []
        for s_map in map_step_result:
            is_struct_like = isinstance(s_map, dict) and "__struct__" in s_map
            if is_struct_like: # item is KEPT
                reject_step_result.append(s_map)
            # Else: item is DISCARDED
        
        # Since reject_step_result will be empty (all states are plain maps):
        if not reject_step_result:
            uniq_step_result_len = 0
        else:
            # This part would run if reject_step_result was not empty
            uniq_step_result_len = len(set(tuple(sorted(s.items())) for s in reject_step_result))
        
        all_non_poi_identical = (uniq_step_result_len == 1)

        if all_non_poi_identical: 
            return {"status": "err", "type": "update_sets_hays_to_same_value", "data": (updates, conditions)}

        return {"status": "ok"}

    def validate_poi_conditions(self, conditions, updates, history, poi, last_poi_state):
        non_poi_people = [p for p in history if p != poi]
        
        non_poi_affected_by_condition = []
        for person in non_poi_people:
            non_poi_last_s = history[person][0]
            matches = True
            if not conditions: # Empty conditions implies matches
                pass
            else:
                for cond_key, cond_val in conditions.items():
                    if non_poi_last_s.get(cond_key) != cond_val:
                        matches = False
                        break
            if matches:
                non_poi_affected_by_condition.append(person)

        if len(non_poi_affected_by_condition) == len(non_poi_people) and non_poi_people: # all non-POIs affected
             # (if all non-POIs meet the condition for the POI update)
            return {"status": "err", "type": "empty_remaining_non_poi", "data": (updates, conditions)}

        if not non_poi_affected_by_condition: # No non-POIs affected, this is fine
            return {"status": "ok"}

        # Some non-POIs are affected by the condition (but not all)
        # Check if these, or others, end up identical to the POI's new state
        
        updated_poi_state = {**last_poi_state, **updates}
        
        similar_to_new_poi_count = 0

        # Non-POIs NOT matching the condition: check if their *current* state (for relevant keys) equals the POI's *update values*
        unaffected_non_pois = [p for p in non_poi_people if p not in non_poi_affected_by_condition]
        for person in unaffected_non_pois:
            non_poi_current_s = history[person][0]
            # Check if this person's relevant attributes already match the POI's *target* update values
            matches_update_target = True
            for upd_key, upd_val in updates.items():
                if non_poi_current_s.get(upd_key) != upd_val:
                    matches_update_target = False
                    break
            if matches_update_target:
                similar_to_new_poi_count +=1
        
        # Non-POIs matching the condition: check if their *updated* state equals POI's *updated* state
        for person in non_poi_affected_by_condition:
            non_poi_last_s = history[person][0]
            updated_non_poi_s = {**non_poi_last_s, **updates}
            if updated_non_poi_s == updated_poi_state:
                similar_to_new_poi_count += 1
        
        num_non_poi_people = len(non_poi_people)
        if num_non_poi_people == 0: # No non-POIs to worry about
             return {"status": "ok"}

        if similar_to_new_poi_count >= num_non_poi_people:
            # Pass some context for potential debugging.
            debug_data = {
                "updates": updates, "conditions": conditions, 
                "non_poi_affected": non_poi_affected_by_condition, 
                "similar_count": similar_to_new_poi_count
            }
            return {"status": "err", "type": "update_makes_all_non_poi_equal_to_poi", "data": debug_data}

        return {"status": "ok"}


    def generate_operation(self, person_to_update, state):
        categories = state['categories']
        difficulty = state['difficulty']
        history = state['history']
        category_defaults = state['category_defaults']
        poi = state['poi']
        
        person_last_state = history[person_to_update][0]
        last_poi_state = history[poi][0] # This is current POI state before this op.
                                         # state['poi_history'][0] is also this.

        num_cond_cat = self.rand_uniform_n(difficulty)
        selected_categories_condition = self.take_random(categories, num_cond_cat)
        
        num_update_cat = self.rand_uniform_n(difficulty)
        selected_categories_update = self.take_random(categories, num_update_cat)

        # Track lengths
        state['statement_condition_length'] = [len(selected_categories_condition)] + state['statement_condition_length']
        state['statement_update_length'] = [len(selected_categories_update)] + state['statement_update_length']

        conditions = {cat: person_last_state[cat] for cat in selected_categories_condition}
        
        updates = {}
        try:
            for category in selected_categories_update:
                current_person_val = person_last_state[category]
                current_poi_val = last_poi_state[category] # POI's value for this category
                
                possible_values = list(category_defaults[category]) # Start with defaults
                
                # Remove person's current value
                if current_person_val in possible_values:
                    possible_values = [v for v in possible_values if v != current_person_val]
                
                # Remove POI's current value
                if current_poi_val in possible_values:
                     possible_values = [v for v in possible_values if v != current_poi_val]

                if not possible_values:
                    return {"status": "err", "type": "cannot_find_new_value_for_update", "data": (updates, conditions)}
                
                updates[category] = random.choice(possible_values)
        except IndexError: # Should be caught by `if not possible_values`
             return {"status": "err", "type": "random_choice_empty_list_in_updates", "data": (updates, conditions)}


        if person_to_update != poi:
            validation_result = self.validate_conditions(conditions, updates, history, poi, last_poi_state)
        else: # person_to_update == poi
            validation_result = self.validate_poi_conditions(conditions, updates, history, poi, last_poi_state)

        if validation_result["status"] == "err":
            return validation_result # Propagate error tuple {status, type, data}

        # Validation OK, proceed
        prospect_history = self.update_history(conditions, updates, history)
        new_poi_state_after_op = prospect_history[poi][0]

        # 1. No non‑POI is allowed to end up identical to the POI
        non_poi_clash = False
        # state['people'] contains all people. state['non_poi_people'] is just non-POIs.
        for p_name in state['people']:
            if p_name != poi: # it's a non-POI
                if prospect_history[p_name][0] == new_poi_state_after_op:
                    non_poi_clash = True
                    break
        
        # 2. For a :hays operation: the chosen non‑POI itself must stay different from the POI
        # (This is covered by non_poi_clash if person_to_update is a non-POI)
        same_as_poi = False
        if person_to_update != poi and prospect_history[person_to_update][0] == new_poi_state_after_op:
            same_as_poi = True

        if non_poi_clash or same_as_poi:
             return {"status": "err", "type": "poi_state_not_unique_after_op", "data": (updates, conditions)}

        # All checks passed, finalize state
        final_new_history = self.update_history(conditions, updates, history)
        new_statement_text = self.formulate_statement(conditions, updates)

        # Prepare the returned new state fragment
        updated_state_fragment = {}
        updated_state_fragment['history'] = final_new_history
        updated_state_fragment['statements'] = [new_statement_text] + state['statements']
        
        current_used_people = state.get('used_people', [])
        updated_state_fragment['used_people'] = [person_to_update] + current_used_people


        if poi == person_to_update:
            updated_state_fragment['poi_history'] = list(final_new_history[person_to_update]) # make copy

        return {"status": "ok", "new_state_fragment": updated_state_fragment}


    def generate_statement(self, current_state):
        
        # Max retries for a single statement generation
        max_iterations = 50 
        
        # These lists are for debugging if max_iterations is reached
        error_history_list = [] 
        update_history_list = []

        for iteration in range(max_iterations + 1):
            operation_type = self.pick_statement_type(current_state)
            
            current_state['operation_types'] = [operation_type] + current_state.get('operation_types', [])
            
            result = self.next_operation(operation_type, current_state)

            if result["status"] == "ok":
                # Merge the fragment into current_state
                current_state.update(result["new_state_fragment"])
                current_state[operation_type] -= 1 # Decrement 'needles' or 'hays' counter
                return current_state # Successfully generated a statement
            else: # result["status"] == "err"
                # Log error and update for potential debug, then retry
                error_history_list.insert(0, result["type"]) # Prepend
                update_history_list.insert(0, result.get("data", {})) 
                
                if iteration >= max_iterations:
                    print("Error: Max iterations reached in generate_statement.", file=sys.stderr)
                    print("Debug Information (last error first):", file=sys.stderr)
                    for u, e in zip(update_history_list, error_history_list):
                        print(f"  Update context: {u}, Error: {e}", file=sys.stderr)
                    
                    print(f"Failing operation type: {operation_type}", file=sys.stderr)
                    # print(f"State at failure: {current_state}", file=sys.stderr) 
                    print(f"Last error type: {result['type']}", file=sys.stderr)
                    print(f"Last error data: {result.get('data', {})}", file=sys.stderr)
                    sys.exit("Exiting due to too many errors in statement generation.")
                
        # Should not be reached if sys.exit happens, but as a fallback:
        raise Exception("Failed to generate statement after max retries, and didn't exit.")


    def create_initialization_statement(self, person, person_init_state):
        property_keys = list(person_init_state.keys())
        random.shuffle(property_keys)

        clauses = []
        for key in property_keys:
            value = person_init_state[key]
            clause = ""
            if key == "location": clause = f"is located at the {value}"
            elif key == "clothes_shirt": clause = f"is wearing a {value} shirt"
            elif key == "clothes_pant": clause = f"is wearing a {value} pant"
            elif key == "clothes_hat": clause = f"is wearing a {value} hat"
            elif key == "clothes_socks": clause = f"is wearing {value} socks"
            elif key == "clothes_gloves": clause = f"is wearing {value} gloves"
            elif key == "clothes_underwear": clause = f"is wearing {value} underwear"
            elif key == "hair": clause = f"has {value} colored hair"
            elif key == "recent_eat": clause = f"last ate a {value}"
            elif key == "recent_watch": clause = f"last watched a {value} movie"
            elif key == "recent_listen": clause = f"last listened to {value} music"
            elif key == "recent_read": clause = f"last read a {value} book"
            clauses.append(clause)
        
        init_statement_text = " and ".join(clauses)
        return f"{person} {init_statement_text}."

    def output(self, final_state):
        history = final_state['history']
        poi = final_state['poi']
        statements_list = final_state['statements'] # Newest statement is at index 0
        poi_history_list = final_state['poi_history'] # Newest POI state is at index 0
        
        used_people_ordered_unique = list(dict.fromkeys(final_state.get('used_people', [])))

        task_description = "Solve this logic puzzle. You MUST finalize your response with a single sentence about the asked property (eg \"Peter is in the livingroom.\", \"Peter is wearing blue socks\",.. ). Solve the puzzle by reasoning through the statements in a strictly sequential order :"

        last_poi_actual_state = poi_history_list[0] # Newest state of POI
        
        target_category = random.choice(list(last_poi_actual_state.keys()))
        target_value = last_poi_actual_state[target_category]

        initialization_texts = []
        for person_name in used_people_ordered_unique:
            person_original_state = history[person_name][-1] # oldest state
            initialization_texts.append(self.create_initialization_statement(person_name, person_original_state))
        
        full_init_block = "\n".join(initialization_texts)

        problem_statement_texts = []
        # Statements are currently newest first; reverse for chronological display
        for idx, stmt_text in enumerate(reversed(statements_list)):
            problem_statement_texts.append(f"{idx + 1}. {stmt_text}")
        
        full_problem_block = "\n".join(problem_statement_texts)
        
        question = ""
        if target_category == "location": question = f"Where is {poi}?"
        elif target_category == "clothes_shirt": question = f"What color shirt is {poi} wearing?"
        elif target_category == "clothes_pant": question = f"What color pant is {poi} wearing?"
        elif target_category == "clothes_hat": question = f"What color hat is {poi} wearing?"
        elif target_category == "clothes_socks": question = f"What color of socks is {poi} wearing?"
        elif target_category == "clothes_gloves": question = f"What color of gloves is {poi} wearing?"
        elif target_category == "clothes_underwear": question = f"What color of underwear is {poi} wearing?"
        elif target_category == "hair": question = f"What is the final hair color of {poi}?"
        elif target_category == "recent_eat": question = f"What did {poi} most recently eat?"
        elif target_category == "recent_watch": question = f"What kind of movie did {poi} most recently watch?"
        elif target_category == "recent_listen": question = f"What kind of music did {poi} most recently listen to?"
        elif target_category == "recent_read": question = f"What kind of book did {poi} most recently read?"

        puzzle_text = f"{task_description}\n\n{full_init_block}\n{full_problem_block}\n\n{question}"
        return puzzle_text, target_value


    def generate(self):
        self._seed_rng(self.original_seed)

        test_categories = ["cogniload"]

        for test_category_name in test_categories:
            Path(f"exp/{test_category_name}").mkdir(parents=True, exist_ok=True)
            Path(f"meta/{test_category_name}").mkdir(parents=True, exist_ok=True)

            configurations = self.make_configs(self.num_grid, self.ratio_grid, self.difficulty_grid)

            for config in configurations:
                num_statements = config['num_statements']
                needles = config['needles']
                difficulty = config['difficulty']

                for _pn in range(self.number_of_puzzles):
                    puzzle_id = random.randint(100_000, 999_999)
                    current_puzzle_seed = puzzle_id # Use puzzle_id as seed for this puzzle
                    self._seed_rng(current_puzzle_seed)

                    hays = num_statements - needles
                    
                    # Select categories for this puzzle
                    puzzle_cats = self.take_random(self.CATEGORIES_LIST, difficulty)

                    # Select people for this puzzle, Special handling for difficulty == 1
                    temp_people_list = self.take_random(self.PEOPLE, difficulty)
                    if difficulty == 1 and temp_people_list: # Ensure list is not empty
                        only_person = temp_people_list[0]
                        # Add a spare person
                        remaining_people = [p for p in self.PEOPLE if p not in temp_people_list]
                        if remaining_people: # Ensure there are spare people
                            spare_person = random.choice(remaining_people)
                            puzzle_people = [only_person, spare_person]
                        else: # Not enough unique people, just use the one.
                            puzzle_people = [only_person]
                    elif not temp_people_list: # If difficulty is low and self.PEOPLE is small
                        # This case means we couldn't pick enough people. Fallback or error.
                        # If difficulty > 0, temp_people_list should have at least one if self.PEOPLE is not empty.
                        # This path is impossible given the size of self.PEOPLE
                        if not self.PEOPLE:
                            print("Error: No people defined.", file=sys.stderr)
                            sys.exit(1)
                        puzzle_people = self.take_random(self.PEOPLE, 1) # at least one person
                        if not puzzle_people: # Still no one, major issue
                             print(f"Error: Could not select any people even with difficulty {difficulty}", file=sys.stderr)
                             continue # Skip this puzzle iteration
                    else:
                        puzzle_people = temp_people_list
                    
                    if not puzzle_people: # Safety check if above logic fails
                        print(f"Warning: No people selected for puzzle {puzzle_id}, skipping.", file=sys.stderr)
                        continue


                    poi = random.choice(puzzle_people)
                    non_poi_people = [p for p in puzzle_people if p != poi]

                    # Initial state for the puzzle generation
                    current_state = {
                        **config, # num_statements, needles, difficulty
                        'hays': hays,
                        'poi': poi,
                        'categories': puzzle_cats,
                        'people': puzzle_people,
                        'non_poi_people': non_poi_people,
                        'history': {},
                        'statements': [], # Newest first
                    }
                    
                    current_state = self.initialize_people(current_state)

                    # Generate statements
                    for _i in range(num_statements):
                        current_state = self.generate_statement(current_state)
                    
                    final_state_for_puzzle = current_state # Name clarity

                    puzzle_content, solution_value = self.output(final_state_for_puzzle)
                    
                    puzzle_base_name = f"{num_statements}_{difficulty}_{needles}_{puzzle_id}"

                    # Save meta file (full state)
                    meta_filename = Path(f"meta/{test_category_name}/{puzzle_base_name}_{solution_value}_state.json")
                    try:
                        with open(meta_filename, 'w') as f:
                            json.dump(final_state_for_puzzle, f, indent=2) # Pretty print for readability
                    except TypeError as e:
                        print(f"Error serializing state to JSON for {meta_filename}: {e}", file=sys.stderr)

                    # Save puzzle file
                    puzzle_filename = Path(f"exp/{test_category_name}/{puzzle_base_name}_{solution_value}.txt")
                    with open(puzzle_filename, 'w', encoding='utf-8') as f:
                        f.write(puzzle_content)
        
        print("Generation complete.")


def main():
    parser = argparse.ArgumentParser(description="Generate CogniLoad logic puzzles.")
    parser.add_argument("--original_seed", type=int, default=42,
                        help="Initial seed for the random number generator.")
    parser.add_argument("--number_of_puzzles", type=int, default=100,
                        help="Number of puzzles to generate for each configuration.")
    parser.add_argument("--num_grid", type=int, nargs='+', default=[20, 50, 100, 250],
                        help="List of numbers of statements.")
    parser.add_argument("--ratio_grid", type=int, nargs='+', default=[5, 10, 25, 50, 75, 90, 95],
                        help="List of ratios of needles to hays (percentage).")
    parser.add_argument("--difficulty_grid", type=int, nargs='+', default=[1, 3, 5, 7, 10],
                        help="List of difficulty levels.")

    args = parser.parse_args()

    cogni_load_generator = CogniLoad(
        original_seed=args.original_seed,
        number_of_puzzles=args.number_of_puzzles,
        num_grid=args.num_grid,
        ratio_grid=args.ratio_grid,
        difficulty_grid=args.difficulty_grid
    )

    cogni_load_generator.generate()

if __name__ == "__main__":
    main()