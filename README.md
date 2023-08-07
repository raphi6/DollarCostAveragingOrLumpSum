# DollarCostAveragingOrLumpSum

Using the backtrader library to test Dollar Cost Averaging (DCA) vs Lump Sum investment strategies. These are two basic ways of investing, main idea is to get comfortable with backtrader.

  - class BuyAndHold follows the Lump Sum strategy, investing $100,000 once.
  - class BuyAndBuyMore follows Dollar Cost Averaging strategy, investing $1000 dollars monthly.

Some possibilites:

  - You can play around with different commissions in FixedCommissionScheme class
  - Change monthly investments in DCA with monthly_cash_invested variable.
  - Change investing period under #Import data

Then:
  
  Simply run the ETF.py file to view results.


General Results:

  - Dollar Cost Averaging is a good strategy for the average person as it follows the following Personal Wealth / Equity Curve  (in debt early 20s, then get a job and begin investing little by little)

    
![image](https://github.com/raphi6/DollarCostAveragingOrLumpSum/assets/69864267/227a1654-9ba4-4df4-adba-135ff5003fe5)


  - For a shorter investing periods:

      Dollar Cost Averaging has lower ROI
      BuyAndHold compounds "faster" as you invest more initially

  - For longer time periods:

      Dollar Cost Averaging will tend to have higher ROI
