###################         Main CF       ########################

-----------------------------------------------------------------

*Submit*

-----------------------------------------------------------------

cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_CF25_Au2p227matched \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/CF25_Au2p227matched/IDEA_25CF_Au2p227matched.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched \
OUT_TAG=IDEA_25CF_Au2p227matched_E15000MeV \
N_BINS=50 \
ETA_STEP=1 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=4 \
REQUEST_MEMORY="4 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh





#####Trying a lot of phi bins#######################################


cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_CF25_Au2p227matched_1000bins_50phi \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/CF25_Au2p227matched/IDEA_CF25_Au2p227matched.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi \
OUT_TAG=IDEA_CF25_Au2p227matched_E15000MeV_1000bins_50phi \
N_BINS=1000 \
ETA_STEP=10 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=2 \
REQUEST_MEMORY="4 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh





cd /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi

hadd -f IDEA_CF25_Au2p227matched_E15000MeV_1000bins_50phi_merged.root \
  IDEA_CF25_Au2p227matched_E15000MeV_1000bins_50phi_eta*.root






mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi/IDEA_CF25_Au2p227matched_E15000MeV_1000bins_50phi_merged.root \
  --label CF25_Au2p227matched_1000bins_50phi \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi/final_plots \
  --logy










cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_CF25_Au3p5 \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/CF25_Au3p5/IDEA_CF25_Au3p5.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au3p5 \
OUT_TAG=IDEA_CF25_Au3p5_E15000MeV \
N_BINS=50 \
ETA_STEP=1 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=4 \
REQUEST_MEMORY="8 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh


cd /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au3p5

hadd -f IDEA_CF25_Au3p5_E15000MeV_merged.root \
  IDEA_CF25_Au3p5_E15000MeV_eta*.root


mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au3p5/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au3p5/IDEA_CF25_Au3p5_E15000MeV_merged.root \
  --label CF25_Au3p5 \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au3p5/final_plots \
  --logy











cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_W20_Au0p3_defaultlike \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/W20_Au0p3_defaultlike/IDEA_W20_Au0p3_defaultlike.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike \
OUT_TAG=IDEA_W20_Au0p3_defaultlike_E15000MeV \
N_BINS=50 \
ETA_STEP=1 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=4 \
REQUEST_MEMORY="8 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh




cd /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike

hadd -f IDEA_W20_Au0p3_defaultlike_E15000MeV_merged.root \
  IDEA_W20_Au0p3_defaultlike_E15000MeV_eta*.root





mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/IDEA_W20_Au0p3_defaultlike_E15000MeV_merged.root \
  --label W20_Au0p3_defaultlike \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/final_plots \
  --logy





#################################################
-----------------------------------------------------------------

**Merge**

-----------------------------------------------------------------


cd /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched

hadd -f IDEA_25CF_Au2p227matched_E15000MeV_merged.root IDEA_25CF_Au2p227matched_E15000MeV_eta*.root


-----------------------------------------------------------------

**Plots**

-----------------------------------------------------------------


mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched/IDEA_25CF_Au2p227matched_E15000MeV_merged.root \
  --label 25CF_Au2p227matched \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched/final_plots \
  --logy



####################   Main Tungsten     ######################


-----------------------------------------------------------------

*Submit*

-----------------------------------------------------------------

cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_W20_Au0p3_defaultlike \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/W20_Au0p3_defaultlike/IDEA_20W_Au0p3_defaultlike.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike \
OUT_TAG=IDEA_20W_Au0p3_defaultlike_E15000MeV \
N_BINS=50 \
ETA_STEP=1 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=4 \
REQUEST_MEMORY="4 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh


-----------------------------------------------------------------

**Merge**

-----------------------------------------------------------------


cd /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike

hadd -f IDEA_20W_Au0p3_defaultlike_E15000MeV_merged.root IDEA_20W_Au0p3_defaultlike_E15000MeV_eta*.root


-----------------------------------------------------------------

**Plots**

-----------------------------------------------------------------

mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/IDEA_20W_Au0p3_defaultlike_E15000MeV_merged.root \
  --label 20W_Au0p3_defaultlike \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/final_plots \
  --logy




#################################################

ATTEMPTING TO REPRODUCE OLD PLOTS

#################################################



---------------------------

Submit

---------------------------

cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_IDEA_W_master \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/IDEA_o1_v03W.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/IDEA_W_master \
OUT_TAG=IDEA_o1_v03W_E15000MeV \
N_BINS=50 \
ETA_STEP=1 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=4 \
REQUEST_MEMORY="4 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh


---------------------------

Merge
---------------------------

cd /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_W_master

hadd -f IDEA_o1_v03W_E15000MeV_merged.root IDEA_o1_v03W_E15000MeV_eta*.root

---------------------------

Plot
---------------------------

mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_W_master/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_W_master/IDEA_o1_v03W_E15000MeV_merged.root \
  --label IDEA_o1_v03W \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_W_master/final_plots \
  --logy


---------------------------

2. CF master
XML
---------------------------



/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/IDEA_o1_v03CF.xml


---------------------------
Submit
---------------------------



cd /eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan

chmod +x run_eta_scan_generic.sh submit_all_generic.sh

EOS_BASE=/eos/user/c/cglenn/FCCWork/Testing/material_budget/g4EtaScan \
LOCAL_DIR=$HOME/FCCWork/batch_jobs/material_budget_IDEA_CF_master \
COMPACT_XML=/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/IDEA_o1_v03CF.xml \
OUT_DIR=/eos/user/c/cglenn/batch_outputs/material_budget/IDEA_CF_master \
OUT_TAG=IDEA_o1_v03CF_E15000MeV \
N_BINS=50 \
ETA_STEP=1 \
ETA_RANGE=-2.5,2.5 \
N_PHI=50 \
ENERGY_MEV=15000 \
ORIGIN_MODE=origin \
REQUEST_CPUS=4 \
REQUEST_MEMORY="4 GB" \
JOB_FLAVOUR=tomorrow \
KEY4HEP_RELEASE=2025-05-29 \
STRICT_PARSE=1 \
KEEP_MACRO=0 \
./submit_all_generic.sh


---------------------------

Merge
---------------------------



cd /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_CF_master

hadd -f IDEA_o1_v03CF_E15000MeV_merged.root IDEA_o1_v03CF_E15000MeV_eta*.root


---------------------------

Plot
---------------------------




mkdir -p /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_CF_master/final_plots

python3 /eos/user/c/cglenn/FCCWork/Testing/material_budget/absETATesting/fold_and_plot_abseta_generic.py \
  --input /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_CF_master/IDEA_o1_v03CF_E15000MeV_merged.root \
  --label IDEA_o1_v03CF \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/IDEA_CF_master/final_plots \
  --logy



Monitor either run
watch condor_q

##################################################################################
COMPARE
##################################################################################
A="new"

B="old"

#############Paths to folded root files########


/eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au3p5/final_plots/25CF_3p5umAu_folded_abseta.root
/eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched/final_plots/25CF_Au2p227matched_folded_abseta.root
/eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/final_plots/20W_Au0p3_defaultlike_folded_abseta.root

/eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi/final_plots/CF25_Au2p227matched_1000bins_50phi_folded_abseta.root
/eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike_1000bins_50phi/final_plots/W20_Au0p3_defaultlike_1000bins_50phi_folded_abseta.root


python3 compare_material_budget_roots.py \
  --input-a /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike/final_plots/W20_Au0p3_defaultlike_folded_abseta.root \
  --input-b /eos/user/c/cglenn/batch_outputs/material_budget/pre-fieldwire-fix/W20_Au0p3_defaultlike/final_plots/20W_Au0p3_defaultlike_folded_abseta.root \
  --label-a 20W_Au0p3_defaultlike_new \
  --label-b 20W_Au0p3_defaultlike_old \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/comparisons/20W_Au0p3_defaultlike_new_vs_20W_Au0p3_defaultlike_old \
  --tag 20W_Au0p3_defaultlike_old_vs_20W_Au0p3_defaultlike_new





############After fixing material xml field wire definitions################

/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/CF25_Au2p227matched/IDEA_CF25_Au2p227matched.xml

/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/CF25_Au3p5/IDEA_CF25_Au3p5.xml

/eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/W20_Au0p3_defaultlike/IDEA_W20_Au0p3_defaultlike.xml









python3 make_material_budget_command_txt.py \
  --compact-xml /eos/user/c/cglenn/FCCWork/GithubRepos/k4geoMax/FCCee/IDEA/compact/IDEA_o1_v03/variants/CF25_Au3p5/IDEA_CF25_Au3p5.xml \
  --out-tag CF25_Au3p5








python3 compare_material_budget_roots.py \
  --input-a /eos/user/c/cglenn/batch_outputs/material_budget/CF25_Au2p227matched_1000bins_50phi/final_plots_rebinned25/CF25_Au2p227matched_1000bins_50phi_rebinned25_folded_abseta.root \
  --input-b /eos/user/c/cglenn/batch_outputs/material_budget/W20_Au0p3_defaultlike_1000bins_50phi/final_plots_rebinned25/W20_Au0p3_defaultlike_1000bins_50phi_rebinned25_folded_abseta.root \
  --label-a CF25_Au2p227matched_1000bins_50phi_rebinned25 \
  --label-b W20_Au0p3_defaultlike_1000bins_50phi_rebinned25 \
  --outdir /eos/user/c/cglenn/batch_outputs/material_budget/comparisons/CF25_Au2p227matched_1000bins_50phi_rebinned25_vs_W20_Au0p3_defaultlike_1000bins_50phi_rebinned25 \
  --tag W20_Au0p3_defaultlike_1000bins_50phi_rebinned25_vs_CF25_Au2p227matched_1000bins_50phi_rebinned25