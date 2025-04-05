class BillCalculator:
    def __init__(self):
        # Constants for tariff rates
        self.DOMESTIC_RATE_TIER1 = 1.50
        self.DOMESTIC_RATE_TIER2 = 3.00
        self.DOMESTIC_RATE_TIER3 = 4.50
        self.COMMERCIAL_RATE = 5.00
        self.INDUSTRIAL_RATE_PEAK = 8.00
        self.INDUSTRIAL_RATE_NORMAL = 6.00
        self.SERVICE_CHARGE_PERCENTAGE = 0.05
        
    def calculate_domestic_bill(self, units):
        if units <= 0:
            return 0
        elif units <= 100:
            return units * self.DOMESTIC_RATE_TIER1
        elif units <= 200:
            return 100 * self.DOMESTIC_RATE_TIER1 + (units - 100) * self.DOMESTIC_RATE_TIER2
        else:
            return 100 * self.DOMESTIC_RATE_TIER1 + 100 * self.DOMESTIC_RATE_TIER2 + (units - 200) * self.DOMESTIC_RATE_TIER3
    
    def calculate_commercial_bill(self, units):
        if units <= 0:
            return 0
        return units * self.COMMERCIAL_RATE
    
    def calculate_industrial_bill(self, units, peak_hour_units=0):
        if units <= 0:
            return 0
        normal_units = units - peak_hour_units
        if normal_units < 0:
            normal_units = 0
            peak_hour_units = units
            
        peak_hour_charge = peak_hour_units * self.INDUSTRIAL_RATE_PEAK
        normal_hour_charge = normal_units * self.INDUSTRIAL_RATE_NORMAL
            
        return peak_hour_charge + normal_hour_charge
    
    def calculate_bill(self, customer_type, current_reading, previous_reading, peak_hour_units=0):
        if current_reading < previous_reading:
            raise ValueError("Current reading cannot be less than previous reading")
            
        units = current_reading - previous_reading
            
        if customer_type.lower() == "domestic":
            net_bill = self.calculate_domestic_bill(units)
        elif customer_type.lower() == "commercial":
            net_bill = self.calculate_commercial_bill(units)
        elif customer_type.lower() == "industrial":
            net_bill = self.calculate_industrial_bill(units, peak_hour_units)
        else:
            raise ValueError("Invalid customer type. Must be Domestic, Commercial, or Industrial")
            
        service_charge = net_bill * self.SERVICE_CHARGE_PERCENTAGE
        total_bill = net_bill + service_charge
            
        return {
            "units_consumed": units,
            "net_bill": round(net_bill, 2),
            "service_charge": round(service_charge, 2),
            "total_bill": round(total_bill, 2)
        }
      
