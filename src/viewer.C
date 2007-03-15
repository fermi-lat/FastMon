void viewer(TString filename = "../python/IsocDataFile.root")
{
  TFile *f = new TFile(filename);
  
// Standard Canvas
  hGemConditionSummary = (TH1F*)f->Get("gem_condition_summary");
  hGemDeltaEventTime   = (TH1F*)f->Get("gem_delta_event_time");
  
  hCalTowerCount = (TH1F*)f->Get("cal_tower_count");
  
  TString hname="";
  TH1F *hCalLogCount[16], *hTkrStripCount[16], *hTkrTot[16];
  for(Int_t i=0; i<16; i++)
    {
    hname = "cal_log_count_tower_";
    hname += i;
    hCalLogCount[i] = (TH1F*)f->Get(hname);   

    hname = "tkr_tot_tower_";
    hname += i;
    hTkrTot[i] = (TH1F*)f->Get(hname);   
    
    hname = "tkr_strip_count_tower_";
    hname += i;
    hTkrStripCount[i] = (TH1F*)f->Get(hname);       
    }

//Trending TProfile    
  tCalTowerCount  = (TProfile*)f->Get("trending_cal_tower_count");
  tCalLatLogCount = (TProfile*)f->Get("trending_cal_log_count_lat");


  TProfile *tCalLogCount[16], *tTkrStripCount[16];
  for(Int_t i=0; i<16; i++)
    {
    hname = "trending_cal_log_count_tower_";
    hname += i;
    tCalLogCount[i] = (TProfile*)f->Get(hname);   
    
    hname = "trending_tkr_strip_count_tower_";
    hname += i;
    tTkrStripCount[i] = (TProfile*)f->Get(hname);       
    }

// Standard Canvas
  TCanvas *cLAT = new TCanvas("LATCan","LAT Canvas",30,50,500,650);
    cLAT->Divide(2,2);
    cLAT->cd(1);  hGemConditionSummary->Draw();
    cLAT->cd(2);  hGemDeltaEventTime->Draw();
    cLAT->cd(3);  hCalTowerCount->Draw();

  TCanvas *cCAL = new TCanvas("CALCan","CAL Canvas",30,50,650,700);
    cCAL->Divide(4,4);
    for(Int_t i=0; i<16; i++)
      {
      cCAL->cd(i+1); gPad->SetLogy(1);   
      hCalLogCount[i]->Draw();
      }

  TCanvas *cTKR = new TCanvas("TKRCan","TKR Canvas",30,50,650,700);
    cTKR->Divide(4,4);
    for(Int_t i=0; i<16; i++)
      {
      cTKR->cd(i+1); gPad->SetLogy(1);   
      hTkrStripCount[i]->Draw();   
     }

  TCanvas *cTOT = new TCanvas("TOTCan","TOT Canvas",30,50,650,700);
    cTOT->Divide(4,4);
    for(Int_t i=0; i<16; i++)
      {
      cTOT->cd(i+1);
      hTkrTot[i]->Draw();   
      }

// Trending Canvas
  TCanvas *cTrendLAT = new TCanvas("LATTrendCan","LAT Trending Canvas",50,50,500,650);
    cTrendLAT->Divide(2,2);
    cTrendLAT->cd(1);  tCalTowerCount->Draw();
    cTrendLAT->cd(2);  tCalLatLogCount->Draw();

  TCanvas *cTrendCAL = new TCanvas("CALTrendCan","CAL Trending Canvas",50,50,650,700);
    cTrendCAL->Divide(4,4);
    for(Int_t i=0; i<16; i++)
      {
      cTrendCAL->cd(i+1);
      tCalLogCount[i]->Draw();
      }

  TCanvas *cTrendTKR = new TCanvas("TKRTrendCan","TKR Trending Canvas",50,50,650,700);
    cTrendTKR->Divide(4,4);
    for(Int_t i=0; i<16; i++)
      {
      cTrendTKR->cd(i+1);
      tTkrStripCount[i]->Draw();   
     }

}
