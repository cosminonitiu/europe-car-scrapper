import { HttpClient, HttpParams } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "src/environments/environment";
import Car from "src/app/shared/models/Car";
import { Observable } from "rxjs";
import { CarPaginatedResultWithOptions } from "src/app/shared/models/CarPaginatedResultWithOptions";
import { CarBrand } from "src/app/shared/models/CarBrand";
import { CarEvaluation } from "src/app/shared/models/CarEvaluation";

@Injectable({ providedIn: 'root' })
export class CarsService {
  constructor(public httpClient: HttpClient){ }

  public apiCarsGetPaginated(
    brand: string,
    model: string,
    skip: number,
    take: number,
    sort_col: string,
    sort_dir: string,
    years: number[],
    min_price: number | null,
    max_price: number | null,
    min_mileage: number | null,
    max_mileage: number | null,
    fuel_type: string[],
    transmission: string[],
    sale_type: string[],
    body_style: string[],
    color: string[],
    doors: number[],
    engine_capacity: number[],
    power: number[],
    volan_part: string[],
    used_or_not: string[],
    last_days: number | null,
    selected_site_sources: string[]
    ): Observable<CarPaginatedResultWithOptions> {

    const basePath = environment.apiBaseurl;
    const URL = `${basePath}/main_car_data`;

    let params = new HttpParams();
    params = params.set('user_id', 'kahjsgk2112j@jaskjgaoj2j1j');
    params = params.set('brand', brand);
    params = params.set('model', model);
    params = params.set('skip', skip);
    params = params.set('take', take);
    params = params.set('sort_col', sort_col);
    params = params.set('sort_dir', sort_dir);
    params = params.set('years', years.join(','));
    params = params.set('min_price', min_price ? min_price : '');
    params = params.set('max_price', max_price ? max_price : '');
    params = params.set('min_mileage', min_mileage ? min_mileage : '');
    params = params.set('max_mileage', max_mileage ? max_mileage : '');
    params = params.set('fuel_type', fuel_type.join(','));
    params = params.set('transmission', transmission.join(','));
    params = params.set('sale_type', sale_type.join(','));
    params = params.set('body_style', body_style.join(','));
    params = params.set('color', color.join(','));
    params = params.set('engine_capacity', engine_capacity.join(','));
    params = params.set('doors', doors.join(','));
    params = params.set('power', power.join(','));
    params = params.set('volan_part', volan_part.join(','));
    params = params.set('used_or_not', used_or_not.join(','));
    params = params.set('last_days', last_days ? last_days : '');
    params = params.set('selected_site_sources', selected_site_sources.join(','));

    return this.httpClient.get<CarPaginatedResultWithOptions>(URL, { params: params });
  }

  public apiGetEvaluations(
    brand: string,
    model: string
  ): Observable<any> {
    const basePath = environment.apiBaseurl;
    const URL = `${basePath}/evaluated`;

    let params = new HttpParams();
    params = params.set('brand', brand);
    params = params.set('model', model);

    return this.httpClient.get<any>(URL, { params: params });
  }

  public apiGetEvaluation(
    brand: string,
    model: string,
    car_id: string,
    title: string,
    year: string,
    site_source: string,
    mileage: string,
    description: string,
    engine_capacity: string,
    power: string,
    fuel_type: string,
    body: string,
    transmission: string,
    volan_part: string,
    ): Observable<CarEvaluation> {

    const basePath = environment.apiBaseurl;
    const URL = `${basePath}/evaluate`;

    let params = new HttpParams();
    params = params.set('user_id', 'kahjsgk2112j@jaskjgaoj2j1j');
    params = params.set('car_id', car_id);
    params = params.set('brand', brand);
    params = params.set('model', model);
    params = params.set('year', year);
    params = params.set('title', title);
    params = params.set('country',
      site_source === 'RO-OLX' ? 'Romania' :
      site_source === 'RO-AUTOVIT' ? 'Romania' :
      'Germany'
      );
    params = params.set('mileage', mileage);
    params = params.set('description', description);
    params = params.set('engine_size', engine_capacity);
    params = params.set('power', power);
    params = params.set('fuel_type', fuel_type);
    params = params.set('body', body);
    params = params.set('gear_box', transmission);
    params = params.set('steering_wheel', volan_part);

    return this.httpClient.get<CarEvaluation>(URL, { params: params });
  }

  public apiGetCarBrandsModels(): Observable<CarBrand[]> {
    const basePath = environment.apiBaseurl;
    const URL = `${basePath}/car_brands_models`;
    return this.httpClient.get<CarBrand[]>(URL);
  }

  public apiGetSiteSources(): Observable<string[]> {
    const basePath = environment.apiBaseurl;
    const URL = `${basePath}/site_sources`;
    return this.httpClient.get<string[]>(URL);
  }

}
