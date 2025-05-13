Mix.install([
  {:jason, "~> 1.4"}
])

defmodule CogniLoad do

  @colors ~w(blue red yellow green purple pink orange black white gray)
  @people ~w(Peter Paul Mary John Mark Jeff Craig Daniel Anna Arnoldo Ali Benjamin Joe Donald Mitch Chuck Jack Lucas Jeniffer Adam Greg Allan David Ellen Fred Hank Hubert Ian Ingrid Rebecca Ken Lewis Michael Nathaniel Oliver Russ Steve Sandy Ted Tanya Veronica Vincent Wesley Brad Sam Igor Sue Jan Jeffrey Jacques Debby Olivia Benedict Chris Charles Harry Eli Mahmoud Chen William Linda Elizabeth Robert Jennifer Emily Joseph Thomas Patricia Anthony Jessica Brian Lisa Kevin Karen Laura Eric Stephanie Michelle George Andrew Joshua Amber Timothy Victoria Richard Cynthia Brandon Megan Matthew Nancy Jacqueline Gary Dorothy Edward Kimberly Scott Sara Justin Brittany Ronald Deborah Janet Christopher Alexander Samantha Oscar Cindy Frank Carl Paula Irene Theresa Dennis Ralph Gerald Martin Terry Bryan Lance Corey Casey Brent Derek Travis Austin Victor Jesse Zachary Kyle Aaron Betty Connie Holly Donna Gloria Carla Isabel Sylvia Evelyn Doris Arthur Raymond Harold Lawrence Neil Brenda Tracy Simon Wendy Zoe Ethan Calvin Sean Ruth Sheila Miriam Lorraine Fay Sophie)

  @categories %{
    location: ~w(bathroom livingroom kitchen basement toilet balcony garden pool bedroom store university farm office bank tree museum school airport zoo train bus park butcher library restaurant mall mountain tunnel church river pond harbor taxi gallery bar pizzeria beach gym elevator insurance embassy police hospital festival monument laboratory observatory valley motorway viewpoint synagogue factory castle cave stadium arena cabin plaza amphitheater bridge pier vineyard forest cliff desert creek bay lighthouse orchard resort camp inn motel aquarium bazaar chapel monastery lookout campground retreat dock depot consulate manor theatre cathedral casino lodge mill bakery spa station diner gazebo terrace arcade boardwalk winery hill plateau ridge port oasis market fairground quarry mine grove auditorium cemetery dunes courthouse prison fort granary ranch promenade coliseum field tower pavilion silo bistro labyrinth cafe saloon brewery carnival marina estate safari cottage courtyard waterpark island greenhouse meadow lagoon ford hacienda village marketplace grotto maze golfcourse atrium academy waterfront peninsula cove summit plains),

    clothes_shirt: @colors,
    clothes_pant: @colors,
    clothes_hat: @colors,
    clothes_socks: @colors,
    clothes_gloves: @colors,
    clothes_underwear: @colors,

    hair: @colors,

    recent_eat: ~w(pizza pasta burrito sushi taco burger toast egg banana potatoes),
    recent_watch: ~w(drama comedy thriller romance adventure horror sci-fi action western fantasy documentary mystery crime musical),
    recent_listen: ~w(rock pop country electronic folk jazz blues classical funk ska rap synth disco reaggea),
    recent_read: ~w(fiction mystery novel thriller biography sci-fi non-fiction essay encyclopedia dictionary ),
  }


  @categories_list Map.keys(@categories)

  def generate(%{
        num_grid: num_grid,
        ratio_grid: ratio_grid,
        difficulty_grid: difficulty_grid,
        number_of_puzzles: number_of_puzzles,
        original_seed: original_seed
      }) do
    # original_seed = 42 # REMOVE THIS LINE (or comment out)
    :rand.seed(:exs1024, {original_seed, original_seed, original_seed})


    test_categories = [:cogniload]

    for test_category <- test_categories do

      File.mkdir_p("exp/#{test_category}")
      File.mkdir_p("meta/#{test_category}")

      configurations = make_configs(num_grid, ratio_grid, difficulty_grid)

      Enum.each(configurations, fn %{num_statements: num_statements, needles: needles, difficulty: difficulty} =configuration ->
        Enum.each(1..number_of_puzzles, fn _pn ->
          puzzle_id = seed = Enum.random(100_000..999_999)
          :rand.seed(:exs1024, {seed, seed, seed})
          hays = num_statements - needles


          categories = Enum.take_random(@categories_list, difficulty)

          people =
            case Enum.take_random(@people, difficulty) do
              [only_person] = list when difficulty == 1 ->
                # add a spare person for future :hays updates
                [only_person | Enum.take_random(@people -- list, 1)]
              list ->
                list
            end

          poi = Enum.random(people)
          non_poi_people = List.delete(people,poi)

          state = Map.merge(configuration,
            %{
              poi: poi,
              categories: categories,
              people: people,
              non_poi_people: non_poi_people,
              history: %{},
              statements: [],
              hays: hays
            })

          state = initialize_people(state)

          final_state = Enum.reduce(1..(num_statements),state,
            fn _i, s -> generate_statement(s)  end)


          {puzzle, solution}  =  final_state |> output

          puzzle_name = "#{num_statements}_#{difficulty}_#{needles}_#{puzzle_id}"

          case Jason.encode(final_state) do
            {:ok, json} ->
              File.write("meta/#{test_category}/#{puzzle_name}_#{solution}_state.json", json)
            {:error, reason} -> IO.puts("Error encoding JSON: #{reason}")
          end

          File.write("exp/#{test_category}/#{puzzle_name}_#{solution}.txt", puzzle)
        end)
      end)
    end
  end

  def initialize_people(%{
      people: people,
      categories: categories,
      difficulty: diff,
      poi: poi
    } = state) do

  # 1. choose defaults
  category_defaults =
    Enum.reduce(categories, %{}, fn category, acc ->
      # we want:
      #   - at least 3 values when difficulty == 1
      #   - otherwise the old (difficulty + 1) rule
      #   - never more values than the domain actually contains
      wanted =
        if diff == 1, do: 3, else: diff + 1

      num_defaults =
        min(wanted, length(@categories[category]))

      Map.put(acc, category, Enum.take_random(@categories[category], num_defaults))
    end)


  # 2. build an initial attribute map for **every** person
  initial_history =
    people
    |> Enum.with_index()
    |> Enum.reduce(%{}, fn {person, idx}, acc ->
      attrs =
        Enum.reduce(categories, %{}, fn category, a ->
          defaults = category_defaults[category]
          value    = Enum.at(defaults, rem(idx, length(defaults)))
          Map.put(a, category, value)
        end)

      Map.put(acc, person, [attrs])
    end)

    state
    |> Map.put(:history,      initial_history)
    |> Map.put(:poi_history,  initial_history[poi])
    |> Map.put(:category_defaults, category_defaults)
    |> Map.put(:operation_types, [])
    |> Map.put(:statement_condition_length, [])
    |> Map.put(:statement_update_length, [])
  end


  def pick_statement_type(%{needles: needles, hays: hays}) do
    random = :rand.uniform() # [0.0 1.0]
    total = needles + hays

    cond do
      random > (needles/total) -> :hays
      true -> :needles # else
    end
  end


  def generate_statement(state, iteration \\ 0, errors \\ [], updates \\ []) do
    operation = pick_statement_type(state) # select whether to do :needles or :hays

    state = Map.put(state, :operation_types, [operation | Map.get(state,:operation_types)])
    case next_operation(operation,  state) do
      {:ok, new_state} ->
        Map.merge(state, new_state)
        |> Map.update!(operation, fn e -> e-1 end) # decrement counter
      {:err, error, update} ->

        # Something is going wrong
        if iteration > 50 do
          # Debug information
          Enum.zip([update | updates], [error | errors])
          |> Kernel.dbg()
          Kernel.dbg(operation)
          Kernel.dbg(state)
          Kernel.dbg(error)

          Kernel.dbg(update)
          exit(1)

        end
        generate_statement(state, iteration + 1, [error | errors], [update | updates])  # if error -> generate different statement
    end
  end


  def next_operation(:needles, %{poi: poi} = state),
    do: generate_operation(poi, state)

  def next_operation(:hays, %{non_poi_people: people} = state),
    do: generate_operation(people |> Enum.random, state)


  def make_configs(num_statements_list, ratio_percent_list, difficulty_list) do
    for n      <- num_statements_list,
        ratio  <- ratio_percent_list,
        diff   <- difficulty_list do
      needles =
        n * ratio / 100
        |> Float.round()
        |> round()
        |> max(1)            # always at least one needle
        |> min(n)            # never more needles than statements

      %{num_statements: n, needles: needles, difficulty: diff}
    end
  end

  def generate_operation(person, %{poi: poi, statement_condition_length: statement_condition_length, statement_update_length: statement_update_length, non_poi_people: people,poi_history: [last_poi_state | _], statements: statements, categories: categories, category_defaults: category_defaults, history: history, difficulty: dif}=state) do
    selected_categories_condition = Enum.take_random(categories,:rand.uniform(dif))
    selected_categories_update = Enum.take_random(categories,:rand.uniform(dif))

    # to track how long the updates and conditions are
    state = state
    |> Map.put(:statement_condition_length, [length(selected_categories_condition) | statement_condition_length])
    |> Map.put(:statement_update_length, [length(selected_categories_update) | statement_update_length])

    [person_last_state | _] = Map.get(history, person)

    conditions = Enum.reduce(selected_categories_condition, %{}, fn category, acc ->
      Map.put(acc, category, Map.get(person_last_state, category))
    end)

    updates = Enum.reduce(selected_categories_update, %{}, fn category, acc ->
      new_value = Map.get(category_defaults,category)
      |> List.delete(Map.get(person_last_state, category))
      |> List.delete(Map.get(last_poi_state, category))
      |> Enum.random()

      Map.put(acc, category, new_value)
    end)

    cond do
      person != poi -> validate_conditions(conditions, updates, history, poi, last_poi_state)
      person == poi -> validate_poi_conditions(conditions, updates, history, poi, last_poi_state)
    end
    |> case do
      {:err, _, _} = err -> err
      {:ok} ->

        prospect_history = update_history(conditions, updates, history)
        new_poi_state    = prospect_history[poi] |> hd()

        # 1. No non‑POI is allowed to end up identical to the POI
        non_poi_clash? =
          people
          |> Enum.reject(&(&1 == poi))
          |> Enum.any?(fn p -> hd(prospect_history[p]) == new_poi_state end)

        # 2. For a :hays operation: the chosen non‑POI itself must
        #    stay different from the POI as well
        same_as_poi? =
          person != poi and
            hd(prospect_history[person]) == new_poi_state

        if non_poi_clash? or same_as_poi? do
          {:err, :poi_state_not_unique, {updates, conditions}}
        else
          # generate statement
          new_history = update_history(conditions, updates, history)
          new_statement = formulate_statement(conditions, updates)

          used_people = Map.get(state,:used_people,[])

          new_state = cond do
            poi == person ->
              Map.put(state, :poi_history, Map.get(new_history,person))
            true ->
              state
          end
          |> Map.put(:history, new_history)
          |> Map.put(:used_people, [person | used_people])
          |> Map.put(:statements, [new_statement | statements])


          {:ok, new_state}
        end



    end
  end


  def formulate_statement(conditions, updates) do

    sentence = []
    condition_keys = Map.keys(conditions) |> Enum.shuffle()
    update_keys = Map.keys(updates) |> Enum.shuffle()

    condition_statement = Enum.reduce(condition_keys, sentence, fn cond_key, acc ->

      value = Map.get(conditions,cond_key)
      sentence = case cond_key do
        :location -> "located in the #{value}"
        :clothes_shirt -> "wearing a #{value} shirt"
        :clothes_pant -> "wearing a #{value} pant"
        :clothes_hat -> "wearing a #{value} hat"
        :clothes_socks -> "wearing #{value} socks"
        :clothes_gloves -> "wearing #{value} gloves"
        :clothes_underwear -> "wearing #{value} underwear"
        :hair -> "having #{value} hair"
        :recent_eat -> "which most recently ate #{value}"
        :recent_watch -> "which most recently watched a #{value} movie"
        :recent_listen -> "which most recently listened to #{value} music"
        :recent_read -> "which most recently read a #{value} book"
      end
      acc ++ [sentence]
      # List.
    end)
    |> Enum.join(" and ")

    condition_statement = "The people " <> condition_statement


    update_statement = Enum.reduce(update_keys, [], fn upd_key, acc ->

      value = Map.get(updates,upd_key)
      sentence = case upd_key do
        :location -> "move to the #{value}"
        :clothes_shirt -> "change into a #{value} shirt"
        :clothes_pant -> "change into a #{value} pant"
        :clothes_hat -> "change into a #{value} hat"
        :clothes_socks -> "change into #{value} socks"
        :clothes_gloves -> "put on #{value} gloves"
        :clothes_underwear -> "put on #{value} underwear"
        :hair -> "color their hair to #{value}"
        :recent_eat -> "eat a #{value}"
        :recent_watch -> "watch a #{value} movie"
        :recent_listen -> "listen to #{value} music"
        :recent_read -> "read a #{value} book"
      end
      acc ++ [sentence]
    end)
    |> Enum.join(" and ")

    condition_statement <> " " <> update_statement
  end


  def update_history(conditions, updates, history) do

    Enum.reduce(Map.keys(history), history, fn person, hist ->

      [most_recent_hist | _] = person_history = Map.get(hist, person)

      new_history = Enum.map(Map.keys(conditions), fn condition ->
        Map.get(conditions, condition) == Map.get(most_recent_hist, condition)
      end)
      |> Enum.all?()
      |> case do
        false -> person_history
        true ->
          hist_update = Enum.reduce(Map.keys(updates), most_recent_hist, fn property, pers_hist ->
            Map.put(pers_hist, property, Map.get(updates, property))
          end)
          [hist_update | person_history]
      end

      Map.put(hist, person, new_history)
    end)
  end


  def validate_conditions(conditions, updates ,history, poi, last_poi_state) do

    # Make sure it doesn't affect POI
    Enum.map(Map.keys(conditions), fn condition ->
      Map.get(conditions, condition) == Map.get(last_poi_state, condition)
    end)
    |> Enum.all?()
    |> case do
      true -> {:err, :invalid_non_poi_update_effects_poi, {updates, conditions}}
      false ->
        # Make sure it doesn't change the state of every non-POI to state of POI

        # Get list of non-pois that is affected by update
        non_poi_people = Map.keys(history) |> List.delete(poi)

        non_pois_affected = Enum.map(non_poi_people, fn person ->

          [non_poi_last_state | _] = Map.get(history, person)

          Enum.map(Map.keys(conditions), fn condition ->
            Map.get(conditions, condition) == Map.get(non_poi_last_state, condition)
          end)
          |> Enum.all?()
          |> case do
            false -> nil
            true -> person
          end
        end)
        |> Enum.reject(&is_nil/1)

        case Enum.empty?(non_pois_affected) do
          true -> {:err, :non_poi_statement_affects_nobody, {updates, conditions}}
          false ->


            prospective_states =
              Enum.map(non_pois_affected, fn person ->
                [last | _] = history[person]
                Map.merge(last, updates)             # state *after* the update
              end)

            # 1. Would *every* affected non‑POI equal the POI afterwards?
            all_equal_poi? =
              Enum.all?(prospective_states, &(&1 == last_poi_state))

            # 2. Would *all* non‑POIs (affected OR unaffected) end up identical?
            all_non_poi_identical? =
              Enum.map(history, fn {person, [last | _]} ->
                if person in non_pois_affected, do: Map.merge(last, updates), else: last
              end)
              |> Enum.reject(fn %{__struct__: _} -> false; _ -> true end) # drop POI
              |> Enum.uniq()
              |> length() == 1

            cond do
              all_equal_poi? ->
                {:err, :non_poi_update_makes_all_states_equal_poi,
                {updates, conditions}}

              all_non_poi_identical? ->
                {:err, :update_sets_hays_to_same_value,
                {updates, conditions}}

              true ->
                {:ok}
            end


        end
    end

  end


  def validate_poi_conditions(conditions, updates ,history, poi, last_poi_state) do

    non_poi_people = Map.keys(history) |> List.delete(poi)

    non_poi_affected = Enum.map(non_poi_people, fn person ->

      [non_poi_last_state | _] = Map.get(history, person)

      Enum.map(Map.keys(conditions), fn condition ->
        Map.get(conditions, condition) == Map.get(non_poi_last_state, condition)
      end)
      |> Enum.all?()
      |> case do
        false -> nil
        true -> person
      end
    end)
    |> Enum.reject(&is_nil/1)

    cond do
      length(non_poi_affected) == length(non_poi_people) -> {:err, :empty_remaining_non_poi, {updates, conditions}}
      Enum.empty?(non_poi_affected) -> {:ok}  # doesn't effect non pois
      true ->

        existing_state_checks = Enum.map((non_poi_people -- non_poi_affected), fn person ->
          [non_poi_last_state | _] = Map.get(history, person)


          Map.take(non_poi_last_state, Map.keys(updates)) == updates
        end)

        non_poi_state_checks = Enum.map(non_poi_affected, fn person ->
          [non_poi_last_state | _] = Map.get(history, person)

          # Make sure that the updated state of the non-poi affected by the poi update are different than the updated poi state
          Map.merge(non_poi_last_state, updates) == Map.merge(last_poi_state, updates)
        end)

        similar =
          existing_state_checks ++ non_poi_state_checks
          |> Enum.map(fn
            true -> 1
            false -> 0
          end)
          |> Enum.sum()

        num_non_poi_people = length(non_poi_people)

        cond do
          similar == 0 -> {:ok}
          similar == 1 -> {:ok}
          similar >= num_non_poi_people -> {:err, :update_makes_all_non_poi_equal_to_poi, {updates, conditions,non_poi_affected, similar,existing_state_checks,non_poi_state_checks}}
          true -> {:ok}
        end
    end
  end

  def create_initialization(person,person_init_state) do

    property_keys = Map.keys(person_init_state) |> Enum.shuffle()

    init_statement = Enum.reduce(property_keys, [], fn key, acc ->

      value = Map.get(person_init_state, key)
      sentence = case key do
        :location -> "is located at the #{value}"
        :clothes_shirt -> "is wearing a #{value} shirt"
        :clothes_pant -> "is wearing a #{value} pant"
        :clothes_hat -> "is wearing a #{value} hat"
        :clothes_socks -> "is wearing #{value} socks"
        :clothes_gloves -> "is wearing #{value} gloves"
        :clothes_underwear -> "is wearing #{value} underwear"
        :hair -> "has #{value} colored hair"
        :recent_eat -> "last ate a #{value}"
        :recent_watch -> "last watched a #{value} movie"
        :recent_listen -> "last listened to #{value} music"
        :recent_read -> "last read a #{value} book"
      end
      acc ++ [sentence]
      # List.
    end)
    |> Enum.join(" and ")

    person <> " " <> init_statement <> "."
  end

  def output(%{history: h, poi: p, statements: s, poi_history: poi_history, used_people: used_people}) do
    task = "Solve this logic puzzle. You MUST finalize your response with a single sentence about the asked property (eg \"Peter is in the livingroom.\", \"Peter is wearing blue socks\",.. ). Solve the puzzle by reasoning through the statements in a strictly sequential order :"

    [last_poi_state | _] = poi_history

    target_category = Map.keys(last_poi_state)|> Enum.random()
    target_value = Map.get(last_poi_state,target_category)

    init_statements =
      Enum.uniq(used_people)
      |> Enum.map(fn e ->
        create_initialization(e,List.last(Map.get(h,e)))
      end)
      |> Enum.join("\n")


    problem = s
      |> Enum.reverse()
      |> Enum.with_index(1)
      |> Enum.map(fn {str, index} ->
        "#{index}. #{str}"
      end)
      |> Enum.join("\n")

    question = case target_category do
      :location -> "Where is #{p}?"
      :clothes_shirt -> "What color shirt is #{p} wearing?"
      :clothes_pant -> "What color pant is #{p} wearing?"
      :clothes_hat -> "What color hat is #{p} wearing?"
      :clothes_socks -> "What color of socks is #{p} wearing?"
      :clothes_gloves -> "What color of gloves is #{p} wearing?"
      :clothes_underwear -> "What color of underwear is #{p} wearing?"
      :hair -> "What is the final hair color of #{p}?"
      :recent_eat -> "What did #{p} most recently eat?"
      :recent_watch -> "What kind of movie did #{p} most recently watch?"
      :recent_listen -> "What kind of music did #{p} most recently listen to?"
      :recent_read -> "What kind of book did #{p} most recently read?"
    end


    puzzle = task <> "\n\n"<> init_statements <> "\n" <>problem <> "\n\n" <> question
    {puzzle, target_value}
  end
end

{opts, _, _} =
  System.argv()
  |> OptionParser.parse(
       switches: [
         nums:    :string,
         ratios:  :string,
         diffs:   :string,
         puzzles: :integer,
         seed:    :integer
       ],
       aliases: [n: :nums, r: :ratios, d: :diffs, p: :puzzles, s: :seed]
     )

cli_defaults = %{
    nums:        "20,50,100,250",
    ratios:      "5,10,25,50,75,90,95",
    diffs:       "1,3,5,7,10",
    puzzles:     100,
    seed:        42
  }

cli_config = %{
  num_grid:        (opts[:nums]   || cli_defaults.nums  ) |> String.split(",") |> Enum.map(&String.to_integer/1),
  ratio_grid:      (opts[:ratios] || cli_defaults.ratios) |> String.split(",") |> Enum.map(&String.to_integer/1),
  difficulty_grid: (opts[:diffs]  || cli_defaults.diffs ) |> String.split(",") |> Enum.map(&String.to_integer/1),
  number_of_puzzles: (opts[:puzzles] || cli_defaults.puzzles),
  original_seed:     (opts[:seed]    || cli_defaults.seed)
}

# Call generate with the cli_config map
CogniLoad.generate(cli_config) # MODIFY THIS LINE
