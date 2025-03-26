import {  Component, OnInit, HostListener, ViewChild, AfterViewInit, ChangeDetectorRef  } from '@angular/core';
import { BreakpointObserver,  BreakpointState } from '@angular/cdk/layout';
import { CarsService } from 'src/app/core/services/car.service';
import Car from 'src/app/shared/models/Car';
import { CarPaginatedResultWithOptions } from 'src/app/shared/models/CarPaginatedResultWithOptions';
import { MatExpansionPanel } from '@angular/material/expansion';
import { Subject, debounceTime, firstValueFrom } from 'rxjs';
import { CarBrand } from 'src/app/shared/models/CarBrand';
import { CarEvaluation, CarEvaluationBuyer } from 'src/app/shared/models/CarEvaluation';
import { MatDialog } from '@angular/material/dialog';
import { CarsDialogComponent } from './cars-dialog/cars-dialog.component';

@Component({
  selector: 'app-cars',
  templateUrl: './cars.component.html',
  styleUrls: ['./cars.component.scss']
})
export class CarsComponent implements OnInit, AfterViewInit{

  constructor(
    private breakpointObserver: BreakpointObserver,
    private carService: CarsService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog,
    ){}

  // Data
  public cars: Car[] = [];
  public total_number_of_cars: number = 0;
  public pageSize = 20;
  public skip = 0;
  public loading = false;

  public last_days_options = [1,2,5,10,15,20,30]

  public brandOptions: string[] = []
  public modelOptions = new Map<string, {name: string, total_count: number}[]>()
  public selectedBrand!: string;
  public currentFilteredModels!: {name: string, total_count: number}[];
  public selectedModel!: {name: string, total_count: number};

  public site_source_options: string[] = [];
  public selected_site_sources: string[] = [];

  public sortOptions: string[][] = [['site_source', 'Site'], ['title', 'Title'], ['price', 'Price'], ['year', 'Year'], ['mileage', 'Mileage'], ['created_time','Created Time']]
  public selectedSort: string[] = this.sortOptions[0];
  public sortDirection = 'up';

  // Data for pricing by ai and car vertical
  public pricedCars = new Map<string, CarEvaluation>()
  public isShaking = false;
  public searchedBrandForPricing = '';
  public searchedModelForPricing = '';

  public getPriceRangeMin(carId: string): number | undefined {
    const car = this.pricedCars.get(carId);
    return car ? car['Price Range']['Min'] : undefined;
  }
  public getPriceRangeMax(carId: string): number | undefined {
    const car = this.pricedCars.get(carId);
    return car ? car['Price Range']['Max'] : undefined;
  }
  public calculatePriceSale(min: number | undefined, max: number | undefined, actual_price: number) {
    if (!min || !max){
      return 0
    }
    const diff_avg = max - min;
    const actual_price_diff = actual_price - min;
    return (actual_price_diff / diff_avg) * 100

  }
  public isCarPricedForUser(car_id: string) {
    const searchedCarId = this.pricedCars.get(car_id);
    if(!searchedCarId) {
      return false
    } else {
      const isUserPartOfBuyers = searchedCarId.users.some((u: CarEvaluationBuyer) => u.user_id === 'kahjsgk2112j@jaskjgaoj2j1j')
      if(!isUserPartOfBuyers) {
        return false;
      } else {
        return true;
      }
    }
  }

  public carInfo = (type: string, car_id: string) => this.onCarInfo(type, car_id);

  public onCarInfo(type: string,  car_id: string) {
    this.dialog.open(CarsDialogComponent, {
      panelClass: type === 'Pricing' ? 'dialog-box' : 'giant-dialog-box',
      data: { type: type, info: this.pricedCars.get(car_id) }
    });
  }

  public toggleSortDirection(): void {
    this.sortDirection = this.sortDirection === 'up' ? 'down' : 'up';
    this.filter();
  }

  //Filters for data
  public year: number[] = [];
  public years: number[] = [];
  public price_high: number | null = null;
  public price_low: number | null = null;
  public debounceInputChanged = new Subject();
  public mileage_high: number | null = null;
  public mileage_low: number | null = null;
  public fuel_type: string[] = [];
  public fuel_types: string[] = [];
  public transmission: string[] = [];
  public transmissions: string[] = [];
  public sale_type: string[] = [];
  public sale_types: string[] = [];
  public body_style: string[] = [];
  public body_styles: string[] = [];
  public color: string[] = [];
  public colors: string[] = [];
  public doors: number[] = [];
  public doorsOptions: number[] = [];
  public engine_capacity: number[] = [];
  public engine_capacities: number[] = [];
  public power: number[] = [];
  public powers: number[] = [];
  public volan_part: string[] = [];
  public volan_parts: string[] = [];
  public used_or_not: string[] = [];
  public used_or_nots: string[] = [];
  public last_days: number | null = null;

  async ngOnInit() {
    // Load the necessities, car brands, site sourcess
    await this.loadCarBrands();
    await this.loadSiteSources();
    await this.loadEvaluatedCars()

    // Initial load of items
    await this.loadItems()

    // Initiliaze the subscribe with 500 debounce for filter inputs
    this.debounceInputChanged.pipe(
      debounceTime(500)
    ).subscribe(() => {
      this.filter()
    });
  }

  public async loadCarBrands() {
    this.brandOptions = JSON.parse(JSON.stringify([]));
    this.modelOptions.clear()
    const brandModels$: CarBrand[] = await firstValueFrom(this.carService.apiGetCarBrandsModels());
    for(let i = 0; i < brandModels$.length; i++){
      this.brandOptions.push(brandModels$[i].brand)
      let model_options: {name: string, total_count: number}[] = [];
      for(let j = 0; j < brandModels$[i].models.length; j++){
        model_options.push({name: brandModels$[i].models[j][0], total_count: Number(brandModels$[i].models[j][1])})
      }
      this.modelOptions.set(brandModels$[i].brand, model_options);
    }
    this.selectedBrand = this.brandOptions[0];
    const models = this.modelOptions.get(this.selectedBrand);
    if(models) {
      this.currentFilteredModels = models;
      this.selectedModel = models[0];
    }
  }

  public async loadSiteSources() {
    const siteSources$: string[] = await firstValueFrom(this.carService.apiGetSiteSources());
    this.site_source_options = siteSources$;
    this.selected_site_sources = this.site_source_options;
  }

  public async evaluate_car(car: Car) {
    this.isShaking = true;
    const regex = /<br\s*\/?>/gi; // For description
    const gpt_response = await firstValueFrom(this.carService.apiGetEvaluation(
      this.selectedBrand,
      this.selectedModel.name,
      car.car_id,
      car.title,
      car.year,
      car.site_source,
      car.mileage,
      car.description.replace(regex, '\n'),
      car.enginesize,
      car.engine_power,
      car.fuel_type,
      car.car_body,
      car.gearbox,
      car.steering_wheel
    ))
    this.pricedCars.set(gpt_response.car_id, gpt_response)
    this.isShaking = false;
  }

  public async loadEvaluatedCars() {
    this.pricedCars.clear()
    const evals = await firstValueFrom(this.carService.apiGetEvaluations(this.selectedBrand, this.selectedModel.name))
    function convertObjectToMap(obj: Record<string, any>): Map<string, any> {
      return new Map(Object.entries(obj));
    }
    this.pricedCars = convertObjectToMap(evals);
    this.searchedBrandForPricing = this.selectedBrand;
    this.searchedModelForPricing = this.selectedModel.name;
  }

  // Virtual pagination through scroll
  @HostListener('scroll')
  public async onScroll() {
    const container = document.querySelector('.main-content') as HTMLElement;
    const scrollHeight = container.scrollHeight;
    const scrollTop = container.scrollTop;
    const clientHeight = container.clientHeight;

    // Check if the user has scrolled to the bottom (or near the bottom) of the container
    if (scrollTop + clientHeight >= scrollHeight - 50 && this.skip < this.total_number_of_cars && !this.loading) {
      this.loading = true;
      await this.loadItems();
    }
  }
  public async loadItems() {
    const data = await firstValueFrom(this.carService.apiCarsGetPaginated(
      this.selectedBrand,
      this.selectedModel.name,
      this.skip,
      this.pageSize,
      this.selectedSort[0],
      this.sortDirection,
      this.year,
      this.price_low,
      this.price_high,
      this.mileage_low,
      this.mileage_high,
      this.fuel_type,
      this.transmission,
      this.sale_type,
      this.body_style,
      this.color,
      this.doors,
      this.engine_capacity,
      this.power,
      this.volan_part,
      this.used_or_not,
      this.last_days,
      this.selected_site_sources
      ))

    this.cars = [...this.cars, ...data.entities];
    this.total_number_of_cars = data.total_entities;
    this.skip += this.pageSize;
    this.loading = false

    if(data.options){
      this.years = data.options.years;
      this.fuel_types = data.options.fuel_types;
      this.transmissions = data.options.transmissions;
      this.body_styles = data.options.body_styles;
      this.sale_types = data.options.sale_types.map((v) => v === true ? 'true' : 'false');
      this.colors = data.options.colors;
      this.doorsOptions = data.options.doors;
      this.engine_capacities = data.options.engine_capacities;
      this.powers = data.options.powers;
      this.volan_parts = data.options.volan_parts;
      this.used_or_nots = data.options.used_or_nots;
    }
  }

  public async brandChange() {
    const models = this.modelOptions.get(this.selectedBrand);
    if(models) {
      this.currentFilteredModels = models;
      this.selectedModel = models[0];
      await this.filter()
    }
  }

  // Changes for selects
  public async filter() {
    const container = document.querySelector('.main-content') as HTMLElement;
    container.scrollTo(0,0)
    this.skip = 0;
    this.cars = JSON.parse(JSON.stringify([]));
    await this.loadItems()
    if(this.selectedBrand != this.searchedBrandForPricing || this.selectedModel.name != this.searchedModelForPricing) {
      await this.loadEvaluatedCars()
    }
  }

  public async change_site_source(site: string){
    if(this.selected_site_sources.includes(site)){
      this.selected_site_sources = this.selected_site_sources.filter((s: string) => s !== site)
    } else {
      this.selected_site_sources.push(site)
    }
    await this.filter();
  }

  public inputDebounceTime(event: Event, input: string) {
    const inputValue = (event.target as HTMLInputElement).value;
    if(input === 'price_low'){
      this.price_low = Number(inputValue)
    } else if(input === 'price_high'){
      this.price_high = Number(inputValue)
    } else if(input === 'mileage_low'){
      this.mileage_low = Number(inputValue)
    } else if(input === 'mileage_high'){
      this.mileage_high = Number(inputValue)
    }
    this.debounceInputChanged.next(null);
  }

  public clearFilters(all: boolean, field?: string) {
    if(all){
      this.year = []
      this.price_high = null
      this.price_low = null
      this.mileage_high = null
      this.mileage_low = null
      this.fuel_type = []
      this.transmission = []
      this.sale_type = []
      this.body_style = []
      this.color = []
      this.doors = []
      this.engine_capacity = []
      this.power = []
      this.volan_part = []
      this.used_or_not = []
      this.last_days = null
    }
  }

  // Sidenav Functionality
  public screen1360: boolean = false;
  public screen900: boolean = false;
  public screen720: boolean = false;
  public screenMobile: boolean = false;
  public isSidenavOpen: boolean = true;

  @ViewChild('searchPanel') searchPanel!: MatExpansionPanel;

  public sidenavItems = [
    { icon: 'search', text: 'Refine Search', show: 'left', type: 'expand' },
    { icon: 'star', text: 'Saved Searches', show: 'right', type: 'expand' },
    { icon: 'help', text: 'Help', show: 'right', type: 'link' },
    { icon: 'feedback', text: 'Feedback', show: 'right', type: 'link' },
    { icon: 'link', text: 'More Tools', show: 'right', type: 'link' },
  ];

  public toggleSidenav(state: string) {
    if(this.screen720) {
      if(state === 'open') {
        this.isSidenavOpen = true;
      } else {
        this.searchPanel?.close();
        this.isSidenavOpen = false;
      }
    }
  }

  ngAfterViewInit(): void {
    this.breakpointObserver.observe('(max-width: 1360px) and (min-width: 900px)').subscribe((result: BreakpointState) => {
      this.screen900 = result.matches;
      if(result.matches) {
        this.searchPanel?.open();
        this.cdr.detectChanges();
      }
    });
    this.breakpointObserver.observe('(max-width: 900px) and (min-width: 720px)').subscribe((result: BreakpointState) => {
      this.screen720 = result.matches;
    });
    this.breakpointObserver.observe('(min-width: 1360px)').subscribe((result: BreakpointState) => {
      this.screen1360 = result.matches;
      if(result.matches) {
        this.searchPanel?.open();
        this.cdr.detectChanges();
      }
    });
    this.breakpointObserver.observe('(max-width: 720px)').subscribe((result: BreakpointState) => {
      this.screenMobile = result.matches;
    });
  }

}
