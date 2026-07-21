## Exploration: PDF Template Redesign

### Current State
The current PDF template (`backend/templates/service_order.html`) uses a simplified CSS flexbox layout with basic sections: header, order info, client info, equipment info, technician info, description, diagnosis, solution, parts table, and signatures. The PDF generator (`backend/app/infrastructure/pdf/generator.py`) fetches order, client, equipment, technician, parts, and attachments, then renders the HTML template via WeasyPrint.

### Affected Areas
- `backend/templates/service_order.html` — Complete redesign from flexbox to table-based layout matching Word document
- `backend/app/infrastructure/pdf/generator.py` — Needs to fetch additional data (attachments, QR code) and pass to template
- `backend/app/domain/models/service_order.py` — Needs new fields: requested_by, department, visit_type, equipment_condition, declared_fault, accessories, work_hours, operators_count, kilometers, travel_expenses
- `backend/app/domain/models/service_order_part.py` — Already has required fields (part_name, part_number, quantity, unit_cost)
- `backend/app/application/dtos/service_order.py` — Needs new fields in CreateOrderRequest, UpdateOrderRequest, OrderResponse
- `backend/app/application/services/order_service.py` — Needs to handle new fields in create/update operations
- `backend/app/api/routes/service_orders.py` — No changes needed (uses DTOs)
- `backend/alembic/versions/` — New migration for adding columns to service_orders table
- `backend/app/infrastructure/qr/generator.py` — Already exists, can be used for QR code in PDF

### Approaches
1. **Table-based HTML redesign** — Rewrite template to use HTML tables for precise layout matching Word document
   - Pros: Exact pixel-perfect match to Word document, easier to control spacing and alignment
   - Cons: More verbose HTML, harder to maintain than flexbox
   - Effort: Medium

2. **Flexbox with CSS Grid hybrid** — Use CSS Grid for main layout and flexbox for internal alignment
   - Pros: More modern CSS, easier responsive design
   - Cons: May not match Word document exactly, harder to control exact positioning
   - Effort: Medium

3. **PDF template engine (WeasyPrint + CSS)** — Keep current approach but enhance CSS with table layout
   - Pros: Leverages existing WeasyPrint knowledge, CSS tables work well in PDF
   - Cons: Still requires significant template rewrite
   - Effort: Medium

### Recommendation
**Table-based HTML redesign** — This approach will provide the most accurate match to the Word document layout. The Word document uses tables extensively, and HTML tables in WeasyPrint render consistently for PDF generation. We'll need to:
1. Add new fields to the ServiceOrder model via Alembic migration
2. Update DTOs and service layer to handle new fields
3. Rewrite the HTML template with table-based layout
4. Update PDF generator to fetch and pass additional data (attachments, QR code)
5. Embed logo as base64 or reference local file

### Risks
- **Data migration**: Adding new fields to existing service_orders table requires careful Alembic migration to preserve existing data
- **Logo embedding**: Need to decide between embedding logo as base64 in HTML or referencing file path (base64 is more reliable for PDF generation)
- **QR code generation**: Need to generate QR code for equipment and embed in PDF (already have generator, just need to integrate)
- **PDF rendering**: WeasyPrint may have limitations with complex table layouts or CSS features
- **Backward compatibility**: Existing service orders won't have new fields, need to handle null values gracefully

### Ready for Proposal
Yes — The exploration is complete. The orchestrator should:
1. Confirm the table-based approach is acceptable
2. Proceed with proposal phase to define exact scope and implementation plan
3. Consider splitting into phases: (1) Template redesign only, (2) Add new fields to model/DTOs, (3) Integrate QR code and logo
