#!/usr/bin/python3
# -!- encoding:utf8 -!-

# IMPORTS

#
# Import de la fonction permettant de mettre à jour les dépendances
#
from api.dependencies import update_dependencies
#
# Import des fonctions d'interaction avec les fichiers de données
#
from api.fs.fs import list_static
from api.fs.fs import list_heatmap_grids
from api.fs.fs import list_heatmap_psd
from api.fs.fs import list_database_raw
from api.fs.fs import list_database_pre_psd
from api.fs.fs import list_database_psd
#
# Import des fonctions de pre-processing des données géolocalisées brutes du Grand Lyon
#
from api.maintenance.database.process import process_file
from api.maintenance.database.process import process_all_files
#
# Import des fonction de séparation des données après la phase de preprocessing
#
from api.maintenance.database.splitter import split_on_key
from api.maintenance.database.splitter import split_all
#
# Import des fonction de séparation des données pour extraire les coordonnées
#
from api.maintenance.database.extractor import extract_coords
#
# Import des fonctions de visualisation d'extraits de données
#
from api.maintenance.database.preview import preview_raw
from api.maintenance.database.preview import preview_psd
#
# Import des fonctions pour la récupération des données et de construction de la grille à partir de ces dernières
#
from api.maintenance.heatmap.process_streets import update_streets_data
from api.maintenance.heatmap.process_streets import download_streets_data
from api.maintenance.heatmap.process_streets import process_streets
#
# Import des fonctions permettant de visualiser les données de la grille
#
from api.maintenance.heatmap.drawer import draw_map_part
from api.maintenance.heatmap.drawer import draw_map
from api.maintenance.heatmap.drawer import draw_heatmap_part
#
# Import des fonctions permettant de construire des cartes de chaleur à partir de la grille et des critères
#
from api.maintenance.heatmap.heatmap_creator import gen_heatmap
from api.maintenance.heatmap.heatmap_creator import gen_all_heatmaps
from api.maintenance.heatmap.heatmap_creator import reduce_grid
from api.maintenance.heatmap.heatmap_creator import reduce_all
from api.maintenance.heatmap.heatmap_creator import avg_grid
from api.maintenance.heatmap.heatmap_creator import gen_script
#
# Import de la fonction permettant de générer le fichier statique des zones couvertes par la heatmap
#
from api.maintenance.heatmap.area import generate_areas
#
# Import du dictionnaire de critères
#
from api.criteria.criterias import criterias_dict
#
# Import des modules Python nécessaires
#
import sys
import os


# FUNCTIONS


def abort(msg):
    print('[maintenance.py]> ' + msg)
    print('-----------------------------\n[maintenance.py]> aborted !')
    exit()


def arg_count():
    return len(sys.argv)


def assert_args(min_size, msg):
    if arg_count() < min_size + 1:
        abort(msg)


def arg(idx):
    return sys.argv[idx]

# ------------------------- COMMANDS FUNCTIONS


def cmd_help():
    print("""[maintenance.py]>
------------------------------- HELP -------------------------------
    + help : display this message

    + list <sub_cmd> : list files for the given subcommand
        - sub_cmd :
            + static
            + heatmap_grids
            + heatmap_psd
            + database_raw
            + database_pre_psd
            + database_psd

    + display <sub_cmd> :
        - sub_cmd :
            + raw <database_raw_file>
            + psd <database_psd_file>
            + map_part <heatmap_grid_file>
            + map
            + heatmap_part <gridname> <heatmap_grid_file> <criteria_name>

    + heatmap <sub_cmd> :
        - sub_cmd :
            + gen <heatmap_grid_file> <criteria_name>
            + gen_all
            + reduce <heatmap_grid_file> <int:precision> <enum:method["FGR","QCGR"]>
            + reduce_all <int:precision>
            + avg_geo_delta <heatmap_grid_file>
            + gen_areas
            + gen_script <int:precision> <enum:method["FGR","QCGR"]>

    + database <sub_cmd> :
        - sub_cmd :
            + process_streets
            + process_all_files
            + extract_coords

--------------------------------------------------------------------""")


def cmd_list(sub_cmd):
    files = []
    if sub_cmd == 'static':
        files = list_static()
    elif sub_cmd == 'heatmap_grids':
        files = list_heatmap_grids()
    elif sub_cmd == 'heatmap_psd':
        files = list_heatmap_psd()
    elif sub_cmd == 'database_raw':
        files = list_database_raw()
    elif sub_cmd == 'database_pre_psd':
        files = list_database_pre_psd()
    elif sub_cmd == 'database_psd':
        files = list_database_psd()
    else:
        abort('unknown list subcommand, run "./maintenance.py help" to get a list of subcommands.')
    # print file list
    print('Listing %s files for %s :\n  +    ' % (len(files), sub_cmd) + '\n  +    '.join(files))


def cmd_display(sub_cmd):
    if sub_cmd == 'raw':
        assert_args(3, 'expected : display raw <database_raw_file>')
        preview_raw(arg(3))
    elif sub_cmd == 'psd':
        assert_args(3, 'expected : display psd <database_psd_file>')
        preview_psd(arg(3))
    elif sub_cmd == 'map_part':
        assert_args(3, 'expected : display map_part <heatmap_grid_file>')
        draw_map_part(arg(3))
    elif sub_cmd == 'map':
        draw_map()
    elif sub_cmd == 'heatmap_part':
        assert_args(5, 'expected : display heatmap_part <gridname> <heatmap_grid_file> <criteria_name>')
        draw_heatmap_part(arg(3), arg(4), arg(5))
    else:
        abort('unknown display subcommand, run "./maintenance.py help" to get a list of subcommands.')


def cmd_dependencies(sub_cmd):
    if sub_cmd == 'update':
        update_dependencies()
    else:
        abort('unknown dependencies subcommand, run "./maintenance.py help" to get a list of subcommands.')


def cmd_heatmap(sub_cmd):
    if sub_cmd == 'gen':
        assert_args(4, 'expected : heatmap gen <heatmap_grid_file> <criteria_name>')
        gen_heatmap(arg(3), criterias_dict[arg(4)])
    elif sub_cmd == 'gen_all':
        gen_all_heatmaps()
    elif sub_cmd == 'reduce':
        assert_args(5, 'expected : heatmap reduce <heatmap_grid_file> <int:precision> <enum:method["FGR","QCGR"]>')
        reduce_grid(arg(3), int(arg(4)), arg(5))
    elif sub_cmd == 'reduce_all':
        assert_args(3, 'expected : heatmap reduce_all <int:precision>')
        reduce_all(int(arg(3)))
    elif sub_cmd == 'avg_geo_delta':
        assert_args(3, 'expected : heatmap avg_geo_delta <heatmap_grid_file>')
        avg_grid(arg(2))
    elif sub_cmd == 'gen_areas':
        generate_areas()
    elif sub_cmd == 'gen_script':
        assert_args(4, 'expected : heatmap gen_script <int:precision> <enum:method["FGR","QCGR"]>')
        gen_script(int(arg(3)), arg(4))
    else:
        abort('unknown heatmap subcommand, run "./maintenance.py help" to get a list of subcommands.')


def cmd_database(sub_cmd):
    if sub_cmd == 'process_streets':
        process_streets()
    elif sub_cmd == 'process_all_files':
        process_all_files()
    elif sub_cmd == 'extract_coords':
        extract_coords()
    else:
        abort('unknown database subcommand, run "./maintenance.py help" to get a list of subcommands.')

# ----------------------- SCRIPT

print('[maintenance.py]> working from "%s"\n-----------------------------' % os.getcwd())

# vérification des paramètres
assert_args(1, 'usage : ./maintenance.py <command> [<options>]')
# récupération de la commande
command = arg(1)
# traitement de la commande
if command == 'help':
    cmd_help()
elif command == 'list':
    assert_args(2, 'expected : list <sub_cmd>')
    cmd_list(arg(2))
elif command == 'display':
    assert_args(2, 'expected : display <sub_cmd> ')
    cmd_display(arg(2))
elif command == 'dependencies':
    assert_args(2, 'expected : dependencies <sub_cmd>')
    cmd_dependencies(arg(2))
elif command == 'heatmap':
    assert_args(2, 'expected : heatmap <sub_cmd>')
    cmd_heatmap(arg(2))
elif command == 'database':
    assert_args(2, 'expected : database <sub_cmd>')
    cmd_database(arg(2))
else:
    abort('unknown command !')

print('-----------------------------\n[maintenance.py]> done !')
