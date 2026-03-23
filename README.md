<br/>
<h1 align="center">Exploration of Hill Climbing, Simulated Annealing, and Genetic Algorithms for Class Scheduling Optimization</h1>

<br/>

> By Group 23, Pendaki Handal - IF'23

<br/>

## Description
This repository contains implementations of various local search algorithms to solve a class scheduling optimization problem. The implemented algorithms include:
- Hill Climbing (Steepest Ascent, Sideways Move, Random Restart, Stochastic)
- Simulated Annealing
- Genetic Algorithm

This program aims to generate an optimal class schedule that minimizes time conflicts for students and lecturers, maximizes room utilization, and considers course priority.

<br/>

## Setup and How to Run the Program

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installing Dependencies
```bash
pip install numpy matplotlib
```

### Running the Program
1. Clone this repository and navigate to the root directory:
```bash
git clone <repository-url>
cd Tubes1AI_PendakiHandal
```

2. This repository provides several test cases (`tc1.json` to `tc5.json`) with increasing levels of complexity. If you want to create your own test case, you can define a `.json` file with the following structure:
```json
{
  "course_classes": [
    {
      "code": "IF3071_K01",
      "num_students": 60,
      "credits": 3
    }
  ],
  "rooms": [
    {
      "code": "7609",
      "capacity": 60
    }
  ],
  "students": [
    {
      "student_id": "13523001",
      "courses": ["IF3071_K01", "IF3130_K01"],
      "priority": [1, 2]
    }
  ],
  "lecturer_schedule": [
    {
      "name": "Bu Fariska",
      "teaching": ["IF3071_K01"],
      "unavailable_times": [["Monday", 9], ["Wednesday", 13]]
    }
  ]
}
```

Structure explanation:
- `course_classes`: Array of course classes with code, number of students, and credits
- `rooms`: Array of rooms with code and capacity
- `students`: Array of students with ID, enrolled courses, and priority (1–7, where 1 = highest priority)
- `lecturer_schedule`: Array of lecturers with name, courses taught, and unavailable time slots (format: [["Day", hour]])
  - Day: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
  - Hour: 7–17 (available class hours)

3. Run the main program:
```bash
python src/main.py
```

4. Follow the input instructions provided by the program  

5. If a new window appears displaying result analysis plots, close the window before continuing to use the program

<br/>

## Contributors

| Name | NIM |
|------|-----|
| 13523058 | Noumisyifa Nabila Nareswari |
| 13523072 | Sabilul Huda | 
| 13523108 | Henry Filberto Shinelo | 

