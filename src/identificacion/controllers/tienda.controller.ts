import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Patch,
  Post,
} from '@nestjs/common';
import { CreateTiendaDto, UpdateTiendaDto } from '../dtos';
import { TiendaService } from '../services/tienda.service';

@Controller('tiendas')
export class TiendaController {
  constructor(
    private readonly tiendaService: TiendaService,
  ) {}

  @Post()
  create(@Body() dto: CreateTiendaDto) {
    return this.tiendaService.create(dto);
  }

  @Get()
  findAll() {
    return this.tiendaService.findAll();
  }

  @Get(':id')
  findById(@Param('id') id: string) {
    return this.tiendaService.findById(id);
  }

  @Patch(':id')
  update(
    @Param('id') id: string,
    @Body() dto: UpdateTiendaDto,
  ) {
    return this.tiendaService.update(id, dto);
  }

  @Delete(':id')
  delete(@Param('id') id: string) {
    return this.tiendaService.delete(id);
  }
}