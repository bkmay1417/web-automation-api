# scraper.py
from playwright.async_api import async_playwright
import asyncio
import postgreSQL  # tu módulo para PostgreSQL

async def scrape_products(task_id=None, lookup_key=None):
    """
    Función principal para scrapear productos.
    task_id: identificador del sitio (ej: "saucedemo") - obligatorio
    lookup_key: filtro opcional por nombre de producto
    """
    if not task_id:
        raise ValueError("Debes ingresar un task_id válido, por ejemplo 'saucedemo'")

    # Asegurar que las tablas existan
    postgreSQL.create_database_if_not_exists()
    postgreSQL.create_tables_if_not_exists()

    products = []

    if task_id == "saucedemo":
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Login SauceDemo
            await page.goto("https://www.saucedemo.com/")
            await page.fill("#user-name", "standard_user")
            await page.fill("#password", "secret_sauce")
            await page.click("#login-button")

            # Esperar lista de productos
            await page.wait_for_selector(".inventory_list")
            items = await page.query_selector_all(".inventory_item")

            if lookup_key:
                # Buscar un producto que coincida exactamente con lookup_key
                encontrado = False
                for item in items:
                    name = await (await item.query_selector(".inventory_item_name")).inner_text()
                    if name.lower() == lookup_key.lower():
                        description = await (await item.query_selector(".inventory_item_desc")).inner_text()
                        price_str = await (await item.query_selector(".inventory_item_price")).inner_text()
                        img_rel = await (await item.query_selector(".inventory_item_img img")).get_attribute("src")
                        price = float(price_str.replace("$", ""))


                        products.append({
                            "name": name,
                            "description": description,
                            "price": price,
                            "image_url": img_rel
                        })
                        encontrado = True
                        break  # Solo devolver el primer producto que coincide exactamente

                if not encontrado:
                    # No se encontró ningún producto con ese nombre exacto
                    raise ValueError(f"No se encontró ningún producto con el nombre '{lookup_key}'. Revisá cómo está escrito.")

            else:
                # lookup_key vacío: devolver todos los productos
                for item in items:
                    name = await (await item.query_selector(".inventory_item_name")).inner_text()
                    description = await (await item.query_selector(".inventory_item_desc")).inner_text()
                    price_str = await (await item.query_selector(".inventory_item_price")).inner_text()
			        # Eliminar $ y convertir a float
                    img_rel = await (await item.query_selector(".inventory_item_img img")).get_attribute("src")
                    price = float(price_str.replace("$", "")) 

                    products.append({
                        "name": name,
                        "description": description,
                        "price": price,
                        "image_url": img_rel
                    })

            await browser.close()

    else:
        # Aquí podés agregar scraping para otros sitios en el futuro
        pass

    # Guardar en DB con un job_id único
    import uuid
    job_id = str(uuid.uuid4())
    postgreSQL.create_task(job_id)
    try:
        postgreSQL.insert_data_for_job(job_id, products)
        postgreSQL.update_task_status(job_id, "completed")
    except Exception as e:
        postgreSQL.update_task_status(job_id, "failed", str(e))

    return job_id, products
