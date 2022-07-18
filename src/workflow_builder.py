from pyarrow import Table

def read_to_dataframe(
    dataset: Table,
    label: str # follows naming convention train,valid,test
    ):
    import pandas as pd
    from pyarrow.parquet import write_table
    write_table(dataset, '{}.parquet'.format(label))
    return pd.read_parquet('{}.parquet'.format(label))
    

def get_nvt_workflow():
    import nvtabular.ops as ops
    import numpy as np
    import nvtabular as nvt

    user_id = ["customer_id".upper()] >> ops.Categorify() >> ops.AddMetadata(tags=["user_id", "user"]) 
    user_features = [
        "FN".upper(),
        "Active".upper(),
        "club_member_status".upper(),
        "fashion_news_frequency".upper(),        
        "postal_code".upper()] >> ops.Categorify() >> ops.AddMetadata(tags=["user"])
    
    age_boundaries = list(np.arange(0,100,5))
    user_age = ["age".upper()] >> ops.FillMissing(0) >> ops.Bucketize(age_boundaries) >> ops.Categorify() >> ops.AddMetadata(tags=["user"])
    user_features = user_features + user_age
    
    purchase_month = (
        ["t_dat".upper()] >> 
        ops.LambdaOp(lambda col: col.dt.month) >> 
        ops.Rename(name ='purchase_month')
    )
    
    purchase_year = (
        ["t_dat".upper()] >> 
        ops.LambdaOp(lambda col: col.dt.year) >> 
        ops.Rename(name ='purchase_year')
    )
    
    context_features = (
        (purchase_month + purchase_year) >> ops.Categorify() >>  ops.AddMetadata(tags=["user"])     
    )
        
    item_id = ["article_id".upper()] >> ops.Categorify() >> ops.AddMetadata(tags=["item_id", "item"]) 
    item_features = ["product_code".upper(), 
            "product_type_no".upper(), 
            "product_group_name".upper(), 
            "graphical_appearance_no".upper(),
            "colour_group_code".upper(),
            "perceived_colour_value_id".upper(),
            "perceived_colour_master_id".upper(),
            "department_no".upper(),
            "index_code".upper(),
            "index_group_no".upper(),
            "section_no".upper(),
            "garment_group_no".upper()] >> ops.Categorify() >>  ops.AddMetadata(tags=["item"]) 
    
    item_avg_price = (
        item_id >> ops.JoinGroupby(
            cont_cols=["price".upper()],
            stats=["mean"]
        ) >>
        ops.FillMissing(0) >>
        ops.Normalize() >>
        ops.Rename(name = "avg_price") >>
        ops.AddMetadata(tags=["item"])
    )    
    
    item_features = item_features + item_avg_price

    outputs = user_id + user_features + context_features + item_id + item_features

    workflow = nvt.Workflow(outputs)

    return workflow