import os
from concurrent.futures import ThreadPoolExecutor
import subprocess
env_instance = os.environ.copy()

def run_in_parallel(*tasks):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(task) for task in tasks]
        for future in futures:
            future.result()

def run_command(command, env=env_instance):
    """Run a command with optional environment variables."""
    result = subprocess.run(command, shell=True, env=env)
    if result.returncode != 0:
        print(f"Command failed: {command}")

def graph_gen():
    """Run graph.py"""
    print("Starting graph_gen simulation...")
    run_command('time python3 simulation/graph/graph.py')
    print("graph_gen finished.")
    
def graph_all():
    walk()
    graph_raw_data()
    
def walk():
    """Run walk.py"""
    print("Starting walk simulation...")
    run_command('time python3 simulation/graph/walk.py')
    print("walk finished.")
    
def graph_raw_data():
    print("Starting graph_raw_data simulation...")
    run_command('time python3 simulation/graph/gen_raw_user_data.py')
    print("graph_raw_data execution completed.")

def graph():
    graph_gen()
    walk()
    graph_raw_data()

def intermap():
    print("Starting intermap...")
    run_command('time python3 tracing_algorithm/intermap.py')
    print("Intermap finished.")

def intermap_optimized():
    print("Starting intermap_optimized optimized...")
    run_command('time python3 tracing_algorithm/intermap_optimized.py')
    print("Intermap optimized finished.")

def intermap_new():
    print("Starting intermap_new optimized...")
    run_command('time python3 tracing_algorithm/intermap_new.py')
    print("intermap_new optimized finished.")
    
def intramap():
    print("Starting intramap...")
    run_command('time python3 tracing_algorithm/intramap.py')
    print("Intramap finished.")
    
def intramap_optimized():
    print("Starting intramap_optimized...")
    run_command('time python3 tracing_algorithm/intramap_optimized.py')
    print("intramap_optimized finished.")
    
def intramap_new():
    print("Starting intramap_new...")
    run_command('time python3 tracing_algorithm/intramap_new.py')
    print("intramap_new finished.")
    
def generate_mappings():
    print("Starting generate_mappings...")
    run_command('time python3 tracing_algorithm/generate_mappings.py')
    print("Mappings generated.")
    
def refine_intramap():
    print("Starting refine_intramap...")
    run_command('time python3 tracing_algorithm/refine_intramap.py')
    print("Intramap finished.")

def push_to_mongo():
    """Run SUMO simulation."""
    print("pushing to mongo")
    run_command('time python3 analysis/push_to_mongo.py')
    print("data fed to mongo")
    
def sumo():
    """Run SUMO simulation."""
    print("Starting SUMO simulation...")
    run_command('time python3 simulation/sumo/sumo_simulation.py')
    print("SUMO simulation finished.")
    # filter_users()

def generate_user_data():
    print("Running generate_user_data.py...")
    run_command('time python3 simulation/generate_user_data.py')
    print("generate_user_data.py finished.")

def generate_user_data_proximity():
    print("Running generate_user_data_proximity.py...")
    run_command('time python3 simulation/generate_user_data_proximity.py')
    print("generate_user_data_proximity.py finished.")
    
def generate_sniffer_data():
    print("Running generate_sniffer_data.py...")
    run_command('time python3 simulation/generate_sniffer_data.py')
    run_command('time python3 simulation/filter_sniffer_data.py')
    print("generate_sniffer_data.py finished.")
    
def filter_sniffer_data():
    print("Running filter_sniffer_data.py...")
    run_command('time python3 simulation/filter_sniffer_data.py')
    print("generate_sniffer_data.py finished.")

def user_data():
    """Generate user data and import to MongoDB."""
    print("Starting user data generation...")
    generate_user_data()
    generate_sniffer_data()
    print("User data generation and import finished.")

def intra_filter():
    run_command('time python3 tracing_algorithm/intra_filter.py')
    print("intra_filter.py finished.")

def aggregate():
    """Running aggregation."""
    print("Starting aggregation process...")
    print("Running aggregation.py...")
    run_command("python3 tracing_algorithm/aggregation.py")
    print("aggregation.py finished.")
    
def aggregate_new():
    """Running aggregation."""
    print("Starting aggregation process...")
    print("Running aggregation_new.py...")
    run_command("python3 tracing_algorithm/aggregation_new.py")
    print("aggregation.py finished.")


def tracing_all():
    intermap()
    intramap()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()

def sanity():
    print("sanity started")
    run_command('time python3 analysis/sanity.py')
    print("sanity finished.")

def filter_users_polygon():
    run_command('time python3 simulation/sumo/filter_users_polygon.py')
    print("filter_users_polygon.py finished.")

def filter_users_RI_Count():
    run_command('time python3 simulation/sumo/filter_users_RI_count.py')
    print("filter_users_RI_count.py finished.")

def sumo_filter_users():
    filter_users_polygon()
    filter_users_RI_Count()
    print("Filtering completed")
    
def reconstruction_multi():
    run_command('time python3 reconstruction/reconstruction_tracing_multi.py')
    print("reconstruction_multi.py finished.")

def reconstruction_single():
    run_command('time python3 reconstruction/reconstruction_tracing_single.py')
    print("reconstruction_single.py finished.")

def reconstruction():
    reconstruction_multi()
    reconstruction_single()
    
def plot():
    """Run plotting service."""
    print("Starting plotting service...")
    run_command('python3 modules/plot_reconstruction.py')
    print("plotting service finished.")

def clean():
    """Clean up generated files."""
    run_command('rm -f *.pyc')
    run_command('rm -rf __pycache__')

def clean_all():
    """Clean up generated files."""
    run_command('rm -f *.pyc')
    run_command('rm -rf __pycache__')
    run_command('rm -rf csv/*.csv')
    run_command('rm -rf data/*.csv')
    run_command('rm -rf logs/*.log')
    run_command('rm -rf images/*.pdf')  
    

def partial_reconstruction():
    run_command('python3 reconstruction/reconstruction_precompute_partial.py')


def automate():
    generate_sniffer_data()
    aggregate()
    intramap_new()
    intermap_new()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()
    
def automate1():
    filter_sniffer_data()
    aggregate()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()

def automate2():
    aggregate()
    intramap_new()
    intermap_new()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()

def automate3():
    intramap_new()
    intermap_new()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()

def automate4():
    filter_sniffer_data()
    aggregate()
    intramap_new()
    intermap_new()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()
    
def automate5():
    generate_sniffer_data()
    aggregate()
    intramap_new()
    intermap_new()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()
    
def automate6():
    generate_user_data()
    generate_sniffer_data()
    aggregate()
    intramap_new()
    intermap_new()
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()

def automate7():
    generate_mappings()
    refine_intramap()
    intra_filter()
    reconstruction()
    plot()

def automate8():
    reconstruction()
    plot()

tasks = {
    "sumo": sumo,
    "user_data": user_data,
    "generate_user_data": generate_user_data,
    "generate_user_data_proximity": generate_user_data_proximity,
    "generate_sniffer_data": generate_sniffer_data,
    "aggregate": aggregate,
    "aggregate_new":aggregate_new,
    "plot": plot,
    "clean": clean,
    "tracing_all": tracing_all,
    "partial_reconstruction": partial_reconstruction,
    "clean_all": clean_all,
    "reconstruction": reconstruction,
    "reconstruction_multi": reconstruction_multi,
    "reconstruction_single": reconstruction_single,
    "filter_users_polygon": filter_users_polygon,
    "filter_users_RI_Count": filter_users_RI_Count,
    "sumo_filter_users": sumo_filter_users,
    "graph": graph,
    "walk": walk,
    "graph_raw_data": graph_raw_data,
    "graph_gen": graph_gen,
    "intra_filter": intra_filter,
    "filter_sniffer_data": filter_sniffer_data,
    "intermap": intermap,
    "intramap": intramap,
    "refine_intramap": refine_intramap,
    "push_to_mongo": push_to_mongo,
    "sanity": sanity,
    "intermap_optimized": intermap_optimized,
    "intramap_optimized": intramap_optimized,
    "intermap_new": intermap_new,
    "intramap_new": intramap_new,
    "generate_mappings": generate_mappings,
    "automate": automate,
    "automate1": automate1,
    "automate2": automate2,
    "automate3": automate3,
    "automate4": automate4,
    "automate5": automate5,
    "automate6": automate6,
    "automate7": automate7,
    "automate8": automate8,
    "graph_all": graph_all,
}
