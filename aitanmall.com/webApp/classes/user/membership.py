class Membership():
    def __init__(self, membership_id, membership_name, membership_label, membership_start_date, membership_end_date):
        self.membership_id = membership_id
        self.membership_name = membership_name
        self.membership_label = membership_label
        self.membership_start_date = membership_start_date
        self.membership_end_date = membership_end_date
    #=============================================================================================
    #Accessor
    #=============================================================================================
    def get_membership_id(self):
        return self.membership_id

    def get_membership_name(self):
        return self.membership_name
    
    def get_membership_label(self):
        return self.membership_label

    def get_membership_start_date(self):
        return self.membership_start_date
    
    def get_membership_end_date(self):
        return self.membership_end_date
    #=============================================================================================
    #Mutator
    #=============================================================================================