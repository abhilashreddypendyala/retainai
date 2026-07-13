from fastapi import HTTPException
from typing import List, Optional
from backend.database.connection import get_db_connection, close_db_connection
from backend.schemas.customer import CustomerSummary, CustomerProfile, CustomerListResponse, Customer360Response, OrderSummaryItem, Recommendation

def _generate_recommendation(profile: CustomerProfile) -> Recommendation:
    # Deterministic business rules
    risk = profile.churn_probability >= 0.5
    clv_val = profile.clv
    
    # Threshold for High CLV, let's say $1000 for example, or based on segment
    is_whale = "Whale" in profile.segment or "Loyal" in profile.segment or clv_val > 1000
    
    if risk and is_whale:
        return Recommendation(
            priority="High",
            action="Win-Back Campaign (VIP)",
            reason="High value customer showing severe churn signals.",
            estimated_roi="High"
        )
    elif risk and not is_whale:
        return Recommendation(
            priority="Medium",
            action="Discount Offer (15%)",
            reason="Customer is at risk but CLV is standard.",
            estimated_roi="Medium"
        )
    elif not risk and is_whale:
        return Recommendation(
            priority="Low",
            action="Loyalty Program / Upsell",
            reason="Customer is loyal and high value. Nurture relationship.",
            estimated_roi="High"
        )
    else:
        return Recommendation(
            priority="Low",
            action="Standard Marketing Drip",
            reason="Customer is safe and regular.",
            estimated_roi="Low"
        )

def _get_countries_for_customers(cursor, customer_ids: List[str]) -> dict:
    if not customer_ids:
        return {}
    placeholders = ','.join('?' * len(customer_ids))
    cursor.execute(f"SELECT customer_id, MAX(country) as country FROM transactions WHERE customer_id IN ({placeholders}) GROUP BY customer_id", customer_ids)
    return {row['customer_id']: row['country'] for row in cursor.fetchall()}

def _row_to_summary(row, country: str) -> CustomerSummary:
    return CustomerSummary(
        customer_id=str(row['customer_id']),
        country=country,
        segment=row['segment'] or "Unknown",
        clv=row['clv'],
        churn_probability=row['churn_probability'],
        churn_prediction=row['churn_prediction']
    )

def _row_to_profile(row, country: str) -> CustomerProfile:
    return CustomerProfile(
        customer_id=str(row['customer_id']),
        country=country,
        segment=row['segment'] or "Unknown",
        clv=row['clv'],
        churn_probability=row['churn_probability'],
        churn_prediction=row['churn_prediction'],
        recency=row['recency'],
        frequency=row['frequency'],
        monetary=row['monetary'],
        purchase_frequency=row['purchase_frequency'],
        avg_order_value=row['avg_order_value'],
        customer_lifespan=row['customer_lifespan'],
        item_diversity=row['item_diversity']
    )

def _apply_dynamic_segments_to_rows(rows, sim_risk: Optional[float], sim_clv: Optional[float]):
    if sim_risk is None or sim_clv is None:
        return rows
    
    # Convert sqlite3.Row to dict so we can modify it
    modified_rows = []
    for r in rows:
        row_dict = dict(r)
        prob = row_dict['churn_probability']
        clv = row_dict['clv']
        
        if prob >= sim_risk and clv >= sim_clv:
            row_dict['segment'] = "High-Risk Whales (Immediate Action)"
        elif prob < sim_risk and clv >= sim_clv:
            row_dict['segment'] = "Loyal Champions (Reward/Upsell)"
        elif prob >= sim_risk and clv < sim_clv:
            row_dict['segment'] = "At-Risk Regulars (Automated Win-back)"
        else:
            row_dict['segment'] = "Safe Regulars (Monitor)"
            
        row_dict['churn_prediction'] = 1 if prob >= sim_risk else 0
        modified_rows.append(row_dict)
    return modified_rows

def get_customers(page: int = 1, page_size: int = 50, sim_risk: Optional[float] = None, sim_clv: Optional[float] = None) -> CustomerListResponse:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        total = cursor.fetchone()[0]
        
        offset = (page - 1) * page_size
        
        cursor.execute("""
            SELECT *
            FROM customers
            ORDER BY clv DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        
        rows = cursor.fetchall()
        rows = _apply_dynamic_segments_to_rows(rows, sim_risk, sim_clv)
        
        customer_ids = [str(r['customer_id']) for r in rows]
        country_map = _get_countries_for_customers(cursor, customer_ids)
        
        items = [_row_to_summary(row, country_map.get(str(row['customer_id']), "Unknown")) for row in rows]
        
        return CustomerListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def get_customer_by_id(customer_id: str, sim_risk: Optional[float] = None, sim_clv: Optional[float] = None) -> Customer360Response:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")
            
        # Apply dynamic segmentation
        if sim_risk is not None and sim_clv is not None:
            processed_rows = _apply_dynamic_segments_to_rows([row], sim_risk, sim_clv)
            row = processed_rows[0]
            
        # 1. Base Profile
        cursor.execute("""
            SELECT SUM(total_amount) as total_spend, COUNT(DISTINCT invoice) as total_orders 
            FROM transactions 
            WHERE customer_id = ?
        """, (customer_id,))
        stats = cursor.fetchone()
            
        country_map = _get_countries_for_customers(cursor, [customer_id])
        profile = _row_to_profile(row, country_map.get(customer_id, "Unknown"))
        
        # 2. Fetch All Orders (Grouped by Invoice)
        cursor.execute("""
            SELECT invoice, MAX(date) as date, GROUP_CONCAT(description, ', ') as items, SUM(quantity) as total_items, SUM(total_amount) as total_amount
            FROM transactions
            WHERE customer_id = ?
            GROUP BY invoice
            ORDER BY date DESC
        """, (customer_id,))
        
        tx_rows = cursor.fetchall()
        recent_tx = []
        for tx in tx_rows:
            # Handle potential nulls
            recent_tx.append(OrderSummaryItem(
                invoice=str(tx['invoice']),
                date=str(tx['date'])[:10] if tx['date'] else "Unknown",
                items=str(tx['items']) if tx['items'] else "Unknown",
                total_items_bought=int(tx['total_items']) if tx['total_items'] else 0,
                total_amount=float(tx['total_amount']) if tx['total_amount'] else 0.0
            ))
            
        # 3. Generate Recommendation
        rec = _generate_recommendation(profile)
        
        return Customer360Response(
            customer=profile,
            recent_transactions=recent_tx,
            recommendation=rec
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def search_customers(query: str, sim_risk: Optional[float] = None, sim_clv: Optional[float] = None) -> List[CustomerSummary]:
    if not query:
        return []
        
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT *
            FROM customers
            WHERE customer_id LIKE ?
            ORDER BY clv DESC
        """, (search_term,))
        
        rows = cursor.fetchall()
        rows = _apply_dynamic_segments_to_rows(rows, sim_risk, sim_clv)
        
        customer_ids = [str(r['customer_id']) for r in rows]
        country_map = _get_countries_for_customers(cursor, customer_ids)
        
        return [_row_to_summary(row, country_map.get(str(row['customer_id']), "Unknown")) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def filter_customers(segment: Optional[str] = None, country: Optional[str] = None, churn_prediction: Optional[int] = None, sim_risk: Optional[float] = None, sim_clv: Optional[float] = None) -> List[CustomerSummary]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        
        if segment:
            if sim_risk is not None and sim_clv is not None:
                if "High-Risk Whales" in segment:
                    query += " AND churn_probability >= ? AND clv >= ?"
                    params.extend([sim_risk, sim_clv])
                elif "Loyal Champions" in segment:
                    query += " AND churn_probability < ? AND clv >= ?"
                    params.extend([sim_risk, sim_clv])
                elif "At-Risk Regulars" in segment:
                    query += " AND churn_probability >= ? AND clv < ?"
                    params.extend([sim_risk, sim_clv])
                elif "Safe Regulars" in segment:
                    query += " AND churn_probability < ? AND clv < ?"
                    params.extend([sim_risk, sim_clv])
                else:
                    query += " AND segment = ?"
                    params.append(segment)
            else:
                query += " AND segment = ?"
                params.append(segment)
            
        if churn_prediction is not None:
            if sim_risk is not None:
                if churn_prediction == 1:
                    query += " AND churn_probability >= ?"
                else:
                    query += " AND churn_probability < ?"
                params.append(sim_risk)
            else:
                query += " AND churn_prediction = ?"
                params.append(churn_prediction)
            
        if country:
            query += " AND customer_id IN (SELECT customer_id FROM transactions WHERE country = ?)"
            params.append(country)
            
        query += " ORDER BY clv DESC"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        rows = _apply_dynamic_segments_to_rows(rows, sim_risk, sim_clv)
        
        customer_ids = [str(r['customer_id']) for r in rows]
        country_map = _get_countries_for_customers(cursor, customer_ids)
        
        return [_row_to_summary(row, country_map.get(str(row['customer_id']), "Unknown")) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def get_all_customer_ids() -> List[str]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id ASC")
        return [str(row['customer_id']) for row in cursor.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)
