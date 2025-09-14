from astroquery.gaia import Gaia
import matplotlib.pyplot as plt        

def plot_sampled_spec(inp_table, color = 'blue', title = '', fontsize = 14, show_legend = True, show_grid = True, linewidth = 2, figsize = [20,5], show_plot = True):
    ""
    "RVS & XP sampled spectrum plotter. 'inp_table' MUST be an Astropy-table object."
    ""
    fig      = plt.figure(figsize=figsize)
    xlabel   = f'Wavelength [{inp_table["wavelength"].unit}]'
    ylabel   = f'Flux [{inp_table["flux"].unit}]'
    plt.plot(inp_table['wavelength'], inp_table['flux'], '-', linewidth = linewidth)
    make_canvas(title = title, xlabel = xlabel, ylabel = ylabel, fontsize= fontsize, show_legend=False, show_grid = show_grid)
    if show_plot:
        plt.show()

    return inp_table['wavelength'][inp_table['flux'].argmax()]

def make_canvas(title = '', xlabel = '', ylabel = '', show_grid = False, show_legend = False, fontsize = 12):
    ""
    "Create generic canvas for plots"
    ""
    plt.title(title,    fontsize = fontsize)
    plt.xlabel(xlabel,  fontsize = fontsize)
    plt.ylabel(ylabel , fontsize = fontsize)
    plt.xticks(fontsize = fontsize)
    plt.yticks(fontsize = fontsize)
    if show_grid:
        plt.grid()
    if show_legend:
        plt.legend(fontsize = fontsize*1.25)
            
RA, DEC = 83.7653807994, -32.8617617202 # Il faut mettre les coordonnes du pixel central ici ;)

fov_lsstcomcam = 1.0 # Field of view in degrees (in fact, the real fov is 0.7 for lsstcomcam)

query = f"SELECT designation, source_id, ra, ra_error, dec, dec_error, phot_g_mean_mag, has_xp_sampled \
            FROM gaiadr3.gaia_source \
            WHERE ra BETWEEN {RA - fov_lsstcomcam/2} AND {RA + fov_lsstcomcam/2} \
            AND dec BETWEEN {DEC - fov_lsstcomcam/2} AND {DEC + fov_lsstcomcam/2};"

job     = Gaia.launch_job_async(query)
results = job.get_results()

bright_star = results['phot_g_mean_mag'].argmin()
results = results[bright_star]

# print(results)

if results["has_xp_sampled"]:
    retrieval_type = 'XP_SAMPLED'   # Options are: 'EPOCH_PHOTOMETRY', 'MCMC_GSPPHOT', 'MCMC_MSC', 'XP_SAMPLED', 'XP_CONTINUOUS', 'RVS', 'ALL'
    data_structure = 'INDIVIDUAL'   # Options are: 'INDIVIDUAL' and 'RAW'
    data_release   = 'Gaia DR3'     # Options are: 'Gaia DR3' (default), 'Gaia DR2'

    source_id = int(results['source_id'])
    datalink = Gaia.load_data(ids=[source_id], 
                            data_release=data_release, 
                            retrieval_type=retrieval_type, 
                            data_structure=data_structure)

    dl_keys  = list(datalink.keys())
    print()
    print(f'The following Datalink products have been downloaded:')
    print('-' * 53)
    for dl_key in dl_keys:
        print(f' * {dl_key}')

    dl_key   = dl_keys[0]           # Select an element from the dl_keys() list displayed above
    votable  = datalink[dl_key][0]  # Select the first (and only) element of the list
    votable_data = votable.to_table()

    source_id = votable.get_field_by_id('source_id').values

    title     = f'Spectra: Gaia DR3 {source_id}'
    wavelength = plot_sampled_spec(votable_data, title = title, fontsize = 12, show_legend = True, show_grid = True, figsize = [20,5], linewidth= 3)  

print('\nFinal results :\n')

print(f'RA              = {results["ra"]} +/- {results["ra_error"]}')
print(f'DEC             = {results["dec"]} +/- {results["dec_error"]}')
print(f'Mean G (mag)    = {results["phot_g_mean_mag"]}')

if results["has_xp_sampled"]:
    print(f'Wavelength (nm) = {wavelength}')
